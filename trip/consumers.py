import math
import os
import random
import time
import geopy.distance
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from user.models import Ride


class LiveLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            return False
        else:
            self.live_session = self.scope['url_route']['kwargs']['ride_id']
            self.live_session_group_name = 'channel_%s' % self.live_session
            await self.channel_layer.group_add(
                self.live_session_group_name,
                self.channel_name
            )
            await self.accept()
            await self.channel_layer.group_send(
                self.live_session_group_name,
                {
                    'type': 'send_connection_message',
                    'joined': True
                }
            )

    async def send_connection_message(self, event):
        joined = event['joined']
        ride_id = self.scope['path'].split('/')[-2]

        querystring = {"origin": f"{self.scope['ride_loc']['from_lat']},{self.scope['ride_loc']['from_lon']}", "destination": f"{self.scope['ride_loc']['to_lat']},{self.scope['ride_loc']['to_lon']}"}

        headers = {
            "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
            "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
        }
        response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers, params=querystring).json()
        await self.send(text_data=json.dumps({
            'status': f'user:{self.scope["user"].name} {"just joined" if joined else "left"} live location preview for ride({ride_id})',
            'route': response['route'] if joined and response else {},
            'state': Ride.State.STARTED
        }))

    async def mock_driver_motion(self, passed_index=None):
        print('[+] inside mock_driver_motion')
        if passed_index is None:
            max_radius = 500.0
            # max_radius = math.sqrt(((random.uniform(2, 5)*1000)*2)/2.0)
            offset = 10 ** (math.log10(max_radius/1.11)-5)
            from_mock_lat = self.scope['ride_loc']['from_lat'] + random.sample([1, -1], 1)[0] * offset
            from_mock_lon = self.scope['ride_loc']['from_lon'] + random.sample([1, -1], 1)[0] * offset
            querystring = {
                "origin": f"{from_mock_lat},{from_mock_lon}",
                "destination": f"{self.scope['ride_loc']['from_lat']},{self.scope['ride_loc']['from_lon']}"
            }
            headers = {
                "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
                "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
            }
            response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers, params=querystring).json()
            self.var_response = response
        if self.var_response:
            if passed_index is None:
                distance = int(self.var_response['route']['distance'])
                duration = int(self.var_response['route']['duration'])
                self.mps = distance / duration
                # current_index = 0
                self.distances_between_all_geometry_pairs = []
                self.var_coordinates = self.var_response['route']['geometry']['coordinates']
                for index in range(0, len(self.var_coordinates) - 1):
                    self.distances_between_all_geometry_pairs.append(
                        geopy.distance.distance((self.var_coordinates[index]), (self.var_coordinates[index + 1])))
                print(f'distances_list length: {len(self.distances_between_all_geometry_pairs)}')
                print(self.distances_between_all_geometry_pairs)
                self.current_distance = 0
                self.current_sent_distance = 0
                await self.channel_layer.group_send(
                    self.live_session_group_name,
                    {
                        'type': 'websocket_text',
                        'driver_loc': self.var_coordinates[0],
                        'customer_loc': f"{self.scope['ride_loc']['from_lat']},{self.scope['ride_loc']['from_lon']}",
                        'state': Ride.State.DRIVER_INCOMING,
                        'total_cords': len(self.var_coordinates),
                        'passed_index': 1
                    }
                )
            # for i in range(0, duration, 3):
            #     time.sleep(3)
            else:
                self.current_distance += self.mps * 3
                # if passed_index == len(self.var_coordinates)-1:
                #     await self.channel_layer.group_send(
                #         self.live_session_group_name,
                #         {
                #             'type': 'websocket_text',
                #             'driver_loc': self.var_coordinates[passed_index]
                #         }
                #     )
                #     print(f"{f'index: {passed_index}' : <8} | {f'distance_pop: {self.distances_between_all_geometry_pairs[passed_index-1].meters}': <33} | {f'distance_sent: {self.current_sent_distance}': <33} | {f'distance_travelled: {self.current_distance}': <33}")
                if (self.distances_between_all_geometry_pairs[passed_index-1].meters + self.current_sent_distance) <= self.current_distance:
                    self.current_sent_distance += self.distances_between_all_geometry_pairs[passed_index-1].meters
                    await self.channel_layer.group_send(
                        self.live_session_group_name,
                        {
                            'type': 'websocket_text',
                            'driver_loc': self.var_coordinates[passed_index],
                            'passed_index': passed_index+1
                        }
                    )
                    print(f"{f'index: {passed_index}' : <8} | {f'distance_pop: {self.distances_between_all_geometry_pairs[passed_index-1].meters}': <33} | {f'distance_sent: {self.current_sent_distance}': <33} | {f'distance_travelled: {self.current_distance}': <33}")
                    # current_index += 1
                else:
                    print(f"{f'index: {passed_index}' : <8} | {f'distance_pop: {self.distances_between_all_geometry_pairs[passed_index-1].meters if passed_index != 0 else 0.0} (same)': <33} | {f'distance_sent: {self.current_sent_distance}': <33} | {f'distance_travelled: {self.current_distance}': <33}")
                    await self.channel_layer.group_send(
                        self.live_session_group_name,
                        {
                            'type': 'websocket_text',
                            'driver_loc': self.var_coordinates[passed_index],
                            'passed_index': passed_index
                        }
                    )

    async def disconnect(self, code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_send(
                self.live_session_group_name,
                {
                    'type': 'send_connection_message',
                    'joined': False
                }
            )
            await self.channel_layer.group_discard(
                self.live_session_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if 'mock_driver' in text_data_json and text_data_json['mock_driver']:
            print('mock var found')
            if 'passed_index' in text_data_json:
                await self.mock_driver_motion(int(text_data_json['passed_index']))
            # await self.channel_layer.group_send(
            #     self.live_session_group_name,
            else:
                await self.mock_driver_motion()
        elif 'location' in text_data_json:
            location = text_data_json['location']
            # await self.channel_layer.group_send(
            #     self.live_session_group_name,
            await self.channel_layer.send(
                {
                    'type': 'liveshare_location',
                    'location': location,
                }
            )

    async def liveshare_location(self, event):
        location = event['location']
        await self.send(text_data=json.dumps({
            'location': location,
        }))

    async def websocket_text(self, event):
        location = event['driver_loc']
        if 'state' in event and 'total_cords' in event:
            await self.send(text_data=json.dumps({
                'driver_loc': location,
                'state': event['state'],
                'total_cords': event['total_cords'],
                'customer_loc': event['customer_loc']
            }))
        else:
            await self.send(text_data=json.dumps({
                'driver_loc': location,
                'new_index': int(event['passed_index'])
            }))
