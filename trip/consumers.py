import asyncio
import math
import os
import random
import geopy.distance
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from trip.consumer_models import MockDriverConnectEventResult, MockDriverIncomingInitiateEventResult, \
    MockDriverReadyToPickupEventResult, MockDriverIncomingInProgressEventResult, MockDriverIncomingInitiateEvent, \
    MockDriverChangeSpeedEvent, Events, BroadcastDriverLiveLocationEvent, BroadcastDriverLiveLocationEventResult, \
    IdleDriverConnectEventResult
from uberClone.settings import idle_drivers
from user.models import Ride, Vehicle


class LiveLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.live_session = self.scope['url_route']['kwargs']['ride_id']
        self.live_session_group_name = 'channel_%s' % self.live_session
        await self.channel_layer.group_add(
            self.live_session_group_name,
            self.channel_name
        )
        if not self.scope['user'].is_authenticated:
            print("[+] not authenticated")
            await self.accept()
            await self.channel_layer.send(
                self.channel_name,
                {
                    'type': 'send_connection_message',
                    'auth': False
                }
            )
        else:
            self.mps_speed = 3
            self.mps_sleep = 0.5
            await self.accept()
            await self.channel_layer.group_send(
                self.live_session_group_name,
                {
                    'type': 'send_connection_message',
                    'joined': True
                }
            )

    async def send_connection_message(self, event):
        if 'auth' in event:
            mockDriverConnectEventResult = MockDriverConnectEventResult(
                message="user is not authenticated",
                route={},
                state=None,
                connection=False
            )
            await self.send(text_data=json.dumps(mockDriverConnectEventResult.to_json()))
            await self.channel_layer.group_discard(
                self.live_session_group_name,
                self.channel_name
            )
            await self.close()
            return
        joined = event['joined']
        # ride_id = self.scope['path'].split('/')[-2]
        querystring = {"origin": f"{self.scope['ride']['loc']['from_lat']},{self.scope['ride']['loc']['from_lng']}", "destination": f"{self.scope['ride']['loc']['to_lat']},{self.scope['ride']['loc']['to_lng']}"}
        headers = {
            "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
            "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
        }
        response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers, params=querystring).json()
        route = response['route']
        route['geometry']['coordinates'] = [{'lat': coordinate[0], 'lng': coordinate[1]} for coordinate in response['route']['geometry']['coordinates']]
        mockDriverConnectEventResult = MockDriverConnectEventResult(
            message=f'user:{self.scope["user"].name} {"just joined" if joined else "left"} live location preview for ride({self.scope["ride"]["id"]})',
            route=route if joined and response else {},
            state=self.scope["ride"]["state"]
        )
        await self.send(text_data=json.dumps(mockDriverConnectEventResult.to_json()))

    async def mock_driver_motion(self, event):
        print('[+] inside mock_driver_motion')
        max_radius = 500.0
        # max_radius = math.sqrt(((random.uniform(2, 5)*1000)*2)/2.0)
        offset = 10 ** (math.log10(max_radius/1.11)-5)
        from_mock_lat = event['location']['lat'] if 'location' in event else self.scope['ride']['loc']['from_lat'] + random.sample([1, -1], 1)[0] * offset
        from_mock_lon = event['location']['lng'] if 'location' in event else self.scope['ride']['loc']['from_lng'] + random.sample([1, -1], 1)[0] * offset
        querystring = {
            "origin": f"{from_mock_lat},{from_mock_lon}",
            "destination": f"{self.scope['ride']['loc']['from_lat']},{self.scope['ride']['loc']['from_lng']}"
        }
        headers = {
            "X-RapidAPI-Key": os.getenv('DIRECTION_API_KEY_HEADER', ''),
            "X-RapidAPI-Host": os.getenv('DIRECTION_API_HOST_HEADER', '')
        }
        response = requests.request("GET", os.getenv('DIRECTION_API_ENDPOINT', 'http://localhost:3000/'), headers=headers, params=querystring).json()
        if response:
            distance = int(response['route']['distance'])
            duration = int(response['route']['duration'])
            self.mps = distance / duration
            self.current_index = 1
            self.distances_between_all_geometry_pairs = []
            self.var_coordinates = response['route']['geometry']['coordinates']
            for index in range(0, len(self.var_coordinates) - 1):
                self.distances_between_all_geometry_pairs.append(
                    geopy.distance.distance((self.var_coordinates[index]), (self.var_coordinates[index + 1])))
            self.var_coordinates = [{'lat': coordinate[0], 'lng': coordinate[1]} for coordinate in self.var_coordinates]
            print(f'distances_list length: {len(self.distances_between_all_geometry_pairs)}')
            print(self.distances_between_all_geometry_pairs)
            print(f'len_cords: {len(self.var_coordinates)}')
            print(self.var_coordinates)
            self.current_distance = 0
            self.current_sent_distance = 0
            mockDriverIncomingInitiateEventResult = MockDriverIncomingInitiateEventResult(
                driver_loc=self.var_coordinates[0],
                customer_loc={'lat': self.scope['ride']['loc']['from_lat'], 'lng': self.scope['ride']['loc']['from_lng']},
                total_cords=len(self.var_coordinates),
                route=self.var_coordinates,
                state=self.scope['ride']['state']
            )
            await self.send(text_data=json.dumps(mockDriverIncomingInitiateEventResult.to_json()))
            while True:
                await asyncio.sleep(self.mps_sleep)
                self.current_distance += self.mps * self.mps_speed
                if (self.distances_between_all_geometry_pairs[self.current_index-1].meters + self.current_sent_distance) <= self.current_distance:
                    self.current_sent_distance += self.distances_between_all_geometry_pairs[self.current_index-1].meters
                    if self.current_index == len(self.var_coordinates)-1:
                        print(f'[+] 0 =================== \n [+] self.current_index {self.current_index}')
                        mockDriverReadyToPickupEventResult = MockDriverReadyToPickupEventResult(
                            driver_loc=self.var_coordinates[self.current_index],
                            state=Ride.State.PICKUP_READY
                        )
                        await self.send(text_data=json.dumps(mockDriverReadyToPickupEventResult.to_json()))
                        break
                    else:
                        print(f'[+] 1 =================== \n [+] self.current_index {self.current_index}')
                        mockDriverIncomingInProgressEventResult = MockDriverIncomingInProgressEventResult(driver_loc=self.var_coordinates[self.current_index])
                        await self.send(text_data=json.dumps(mockDriverIncomingInProgressEventResult.to_json()))
                    print(f"{f'index: {self.current_index}' : <8} | {f'distance_pop: {self.distances_between_all_geometry_pairs[self.current_index-1].meters}': <33} | {f'distance_sent: {self.current_sent_distance}': <33} | {f'distance_travelled: {self.current_distance}': <33}")
                    self.current_index += 1
                else:
                    print(f"{f'index: {self.current_index}' : <8} | {f'distance_pop: {self.distances_between_all_geometry_pairs[self.current_index-1].meters if self.current_index != 0 else 0.0} (same)': <33} | {f'distance_sent: {self.current_sent_distance}': <33} | {f'distance_travelled: {self.current_distance}': <33}")
                    if self.current_index == len(self.var_coordinates)-1:
                        print(f'[+] 2 =================== \n [+] self.current_index {self.current_index}')
                        mockDriverReadyToPickupEventResult = MockDriverReadyToPickupEventResult(
                            driver_loc=self.var_coordinates[self.current_index],
                            state=Ride.State.PICKUP_READY
                        )
                        await self.send(text_data=json.dumps(mockDriverReadyToPickupEventResult.to_json()))
                        break
                    else:
                        print(f'[+] 3 =================== \n [+] self.current_index {self.current_index}')
                        mockDriverIncomingInProgressEventResult = MockDriverIncomingInProgressEventResult(driver_loc=self.var_coordinates[self.current_index])
                        await self.send(text_data=json.dumps(mockDriverIncomingInProgressEventResult.to_json()))

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
        print('[+] received json')
        print(text_data_json)
        if 'event' in text_data_json:
            if text_data_json['event'] == Events.MockDriverIncomingInitiateEvent.value:
                mockDriverIncomingInitiateEvent = MockDriverIncomingInitiateEvent(**text_data_json)
                print("[+] mockDriverIncomingInitiateEvent")
                print(mockDriverIncomingInitiateEvent.to_json())
                # await self.mock_driver_motion()
                await self.channel_layer.group_send(
                    self.live_session_group_name,
                    {
                        'type': 'mock_driver_motion',
                        'location': mockDriverIncomingInitiateEvent.request.location
                    }
                )
            elif text_data_json['event'] == Events.BroadcastDriverLiveLocationEvent.value:
                broadcastDriverLiveLocationEvent = BroadcastDriverLiveLocationEvent(**text_data_json)
                await self.channel_layer.group_send(
                    self.live_session_group_name,
                    {
                        'type': 'liveshare_location',
                        'location': broadcastDriverLiveLocationEvent.request.location,
                    }
                )
            elif text_data_json['event'] == Events.MockDriverChangeSpeedEvent.value:
                mockDriverChangeSpeedEvent = MockDriverChangeSpeedEvent(**text_data_json)
                await self.channel_layer.group_send(
                    self.live_session_group_name,
                    {
                        'type': 'change_speed',
                        'new_speed': mockDriverChangeSpeedEvent.request.new_speed,
                        'new_sleep': mockDriverChangeSpeedEvent.request.new_sleep,
                    }
                )

    async def change_speed(self, event):
        self.mps_speed = event['new_speed']
        self.mps_sleep = event['new_sleep']

    async def liveshare_location(self, event):
        broadcastDriverLiveLocationEventResult = BroadcastDriverLiveLocationEventResult(event['location'])
        await self.send(text_data=json.dumps(broadcastDriverLiveLocationEventResult.to_json()))


class IdleDriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope['url_route'])
        self.live_session = self.scope['path'].replace('/', '_')
        self.live_session_group_name = 'channel_%s' % self.live_session
        await self.channel_layer.group_add(
            self.live_session_group_name,
            self.channel_name
        )
        if not self.scope['user'].is_authenticated:
            print("[+] not authenticated")
            await self.accept()
            await self.channel_layer.send(
                self.channel_name,
                {
                    'type': 'send_connection_message',
                    'auth': False
                }
            )
        else:
            self.mps_speed = 3
            self.mps_sleep = 0.5
            await self.accept()
            await self.channel_layer.group_send(
                self.live_session_group_name,
                {
                    'type': 'send_connection_message',
                    'joined': True
                }
            )

    async def send_connection_message(self, event):
        if 'auth' in event:
            idleDriverConnectEventResult = IdleDriverConnectEventResult(
                message="user is not authenticated",
                connection=False,
                error=self.scope['error']
            )
            await self.send(text_data=json.dumps(idleDriverConnectEventResult.to_json()))
            await self.channel_layer.group_discard(
                self.live_session_group_name,
                self.channel_name
            )
            await self.close()
            return
        joined = event['joined']
        idleDriverConnectEventResult = IdleDriverConnectEventResult(
            message=f'driver:{self.scope["user"].name} {"just added to" if joined else "removed from"} idle_driver',
            error=self.scope['error']
        )
        await self.send(text_data=json.dumps(idleDriverConnectEventResult.to_json()))

    async def disconnect(self, code):
        if self.scope['user'].is_authenticated:
            del idle_drivers[f'{self.scope["user"].id}']
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
        print('[+] received json')
        print(text_data_json)
        if 'event' in text_data_json:
            if text_data_json['event'] == Events.BroadcastDriverLiveLocationEvent.value:
                broadcastDriverLiveLocationEvent = BroadcastDriverLiveLocationEvent(**text_data_json)
                await self.channel_layer.group_send(
                    self.live_session_group_name,
                    {
                        'type': 'liveshare_location',
                        'location': broadcastDriverLiveLocationEvent.request.location,
                    }
                )

    async def liveshare_location(self, event):
        loc = event['location']
        loc.update({'user_id': self.scope['user'].id})
        loc.update({'vehicle_type': self.scope['vehicle']['type'] if self.scope['vehicle'] else Vehicle.Type.CAR_SEDAN})
        loc.update({'vehicle_number': self.scope['vehicle']['number'] if self.scope['vehicle'] else None})
        loc.update({'seat_capacity': self.scope['vehicle']['seat_capacity'] if self.scope['vehicle'] else None})
        idle_drivers[f'{self.scope["user"].id}'] = loc
        broadcastDriverLiveLocationEventResult = BroadcastDriverLiveLocationEventResult(event['location'])
        await self.send(text_data=json.dumps(broadcastDriverLiveLocationEventResult.to_json()))
