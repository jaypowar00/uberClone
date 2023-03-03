# UberClone's API Routes

- API Endpoint: <https://uber-clone-v1.onrender.com>

1. `/user`:  
   - method: `GET`
   - header: `Authorization=Token <access_token>`
   - response:  

      ```json
      {
        "status": true,
        "message": "user profile",
        "user": {
          "public_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
          "email": "example@domain.com",
          "name": "ABC PQR XYZ",
          "username": "ABC_e352798536a",
          "address": "AABBCC, XXZZYY",
          "gender": "M",
          "phone": "1212121212",
          "dob": "1997-12-20",
          "account_type": "R",
          "date_joined": "2023-02-28T13:10:39.651231Z",
          "about": "something here"
        }
      }
      ```

2. `/user/register`:
   - method: `POST`
   - body:

      ```json
      {
        "name": "ABC XYZ",
        "email": "example@domain.com",
        "password": "XXX",
        "gender": "M",
        "phone": "1212121212",
        "address": "AABBCC, XXZZYY",
        "account_type": "R"
      }
      ```

   - response:

      ```json
      {
        "status": true,
        "message": "User registered!",
        "context": {
          "name": "ABC XYZ",
          "email": "example@domain.com",
          "gender": "M",
          "phone": "1212121212",
          "address": "AABBCC, XXZZYY",
          "account_type": "R"
        }
      }
      ```

3. `'/user/login`:
   - method: `POST`
   - body:

      ```json
      {
        "email": "jay@gmail.com",
        "password": "pass"
      }
      ```

   - response:

      ```json
      {
        "status": true,
        "message": "Successfully logged in",
        "access_token": "<access_token>",
        "refresh_token": "<refresh_token>",
        "csrf_token": "<csrf_token>",
        "user": {
          "id": 1,
          "public_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
          "email": "example@domain.com",
          "name": "ABC PQR XYZ",
          "username": "ABC_e352798536a",
          "address": "AABBCC, XXZZYY",
          "gender": "M",
          "phone": "1212121212",
          "dob": "1997-12-20",
          "account_type": "R",
          "date_joined": "2023-02-28T13:10:39.651231Z",
          "about": "something here"
        }
      }
      ```

4. `/user/logout`:
   - method: `POST`
   - header:
     - `refreshtoken=<refresh_token>`
     - `Authorization=Token <access_token>`
     - `X-CSRFToken=<csrf_token>`
   - response

      ```json
      {
        "status": true,
        "message": "successfully logged out!"
      }
      ```

5. `/user/update`:
   - method: `PUT`
   - header:
     - `Authorization=Token <access_token>`
     - `X-CSRFToken=<csrf_token>`
   - body:

      ```json
      {
        "email": "example2@domain.com",
        "name": "ABC PQR XYZ",
        "username": "ABC_0001",
        "phone": "9999999999",
        "address": "JJJ KKL",
        "dob": "1997-12-20",
        "about": "new"
      }
      ```

   - response

      ```json
      {
        "status": true,
        "message": "User updated!",
        "context": {
          "email": "example2@domain.com",
          "name": "ABC PQR XYZ",
          "username": "ABC_0001",
          "phone": "9999999999",
          "address": "JJJ KKL",
          "dob": "1997-12-20",
          "about": "new"
        }
      }
      ```

6. `/user/delete`:
   - method: `DELETE`
   - header: 
     - `Authorization=Token <access_token>`
     - `X-CSRFToken=<csrf_token>`
   - response:

      ```json
      {
        "status": true,
        "message": "User profile successfully deleted"
      }
      ```

7. `/user/update-password`:
   - method: `POST`
   - header:
     - `Authorization=Token <access_token>`
     - `X-CSRFToken=<csrf_token>`
   - body:

      ```json
      {
        "old_password": "XXX",
        "new_password": "YYY"
      }
      ```

   - response:

      ```json
      {
        "status": true,
        "message": "Password changed"
      }
      ```

8. `/user/refresh-token`:
   - method: `PUT`
   - header: `refreshtoken=<refresh_token>`
   - response:

      ```json
      {
        "status": true,
        "message": "access token refreshed",
        "access_token": "<access_token>"
      }
      ```

9. `/user/trip/locations`:
   - method: `GET`
   - response:

      ```json
      {
        "status": true,
        "locations": [
          {
            "id": 1,
            "name": "Rankala Lake",
            "address": "Hari Om Nagar, Kolhapur, Maharashtra 416012",
            "thumbnail": "https://lh5.googleusercontent.com/p/AF1QipNB7ncjC0lwJ09WfAZWY-KBawK00GhdcQfcW4wE=w408-h326-k-no",
            "lon": 74.214084,
            "lat": 16.694488,
            "description": "Scenic locale featuring boat rides & lakeside gardens, walking paths & various food vendors.",
            "geo": {
              "country": "India",
              "city": "Kolhapur",
              "district": null,
              "region": "Maharashtra",
              "village": null,
              "state": "Maharashtra",
              "display_address": "Rankala Choupati, NH166G, Kolhapur, Maharashtra, 416012, India",
              "postcode": "416012",
              "place_id": 12627927,
              "accuracy": 0.001
            }
          }
        ],
      }
      ```

10. `/user/trip/get-location-path`:
    - method: `GET`
    - header: `Authorization=Token <access_token>`
    - body:

      ```json
      {
        "from_lat": 16.700947,
        "from_lon": 74.216508,
        "to_trip": 1
      }
      ```

      or

      ```json
      {
        "from_lat": 16.700947,
        "from_lon": 74.216508,
        "to_lat": 16.694488,
        "to_lon": 74.214084
      }
      ```
    - response:

      ```json
      {
        "status": true,
        "route": {
          "distance": 987,
          "duration": 197,
          "bounds": {
            "south": 16.694705,
            "west": 74.213868,
            "north": 16.700868,
            "east": 74.216535
          },
          "geometry": {
            "coordinates": [
              [
                16.700828,
                74.216535
              ],
              ...
              ,
              [
                16.694705,
                74.214092
              ]
            ]
          },
          "steps": [
            {
              "distance": 181,
              "duration": 35,
              "start_point_index": 0,
              "start_point": {
                "lat": 16.700828,
                "lng": 74.216535
              },
              "end_point_index": 15,
              "end_point": {
                "lat": 16.700532,
                "lng": 74.215148
              },
              "bounds": {
                "south": 16.700532,
                "west": 74.215138,
                "north": 16.700868,
                "east": 74.216535
              }
            },
            ...
            ,
            {
              "distance": 15,
              "duration": 4,
              "start_point_index": 65,
              "start_point": {
                "lat": 16.694705,
                "lng": 74.214234
              },
              "end_point_index": 66,
              "end_point": {
                "lat": 16.694705,
                "lng": 74.214092
              },
              "bounds": {
                "south": 16.694705,
                "west": 74.214092,
                "north": 16.694705,
                "east": 74.214234
              },
              "maneuver": "turn right"
            }
          ]
        }
      }
      ```
