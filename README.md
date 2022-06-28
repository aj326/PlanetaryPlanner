Document project description in README file, including the following information:
    URL location for the hosted API

# Planetary Planner
This project is a planner based on the [planetary hours](https://en.wikipedia.org/wiki/Planetary_hours) for a given time and location.
What motivated me to dream this up is my recent fascination with the planets and the stars. Developing this code has helped appreciate python's ease quite a bit. The way Python handles dates is user-friendly, and the available modules, like [astral](https://pypi.org/project/astral/), and [pytz](https://pypi.org/project/pytz/) **greatly** sped up development time.
## URL

https://planetary-planner.herokuapp.com

### Install Dependencies

1. **Python 3.10** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by running:

```bash
pip install -r requirements.txt
```

### Set up the Database
Make sure postgres is [running](https://www.postgresqltutorial.com/), then from the command line, run:

```bash
psql < planetary_planner.psql
psql < test_planetary_planner.psql
```
 You can manually populate the database, or populate it with curl commands.
 
### Authentication
There are two roles: admin and client. For testing porpuses, I set up two accounts:
- Admin - admin@test.com PA$$word
- Client - client@test.com

The root dir of the server will show you the access token to use in [unit testing module:39](./test_all.py):

<img src="/home/aj/PycharmProjects/PlanetaryPlanner/static/Screenshot from 2022-06-28 13-35-35.png"/>

### Endpoints Details

`GET '/users'`
*admin only*
returns json object of users with full details, as such
```json
{
    "success": true,
    "users": [
        {
            "events": null,
            "id": 22,
            "location": {
                "city": "Chicago",
                "latitude": 41.833333333333336,
                "longitude": -87.68333333333334,
                "region": "USA",
                "timezone": "US/Central"
            },
            "username": "ahmed.jehairan@protonmail.com"
        },
        {
            "events": null,
            "id": 23,
            "location": null,
            "username": "testme@this.com"
        }
    ]
}
```
`GET '/users/{id}/location'`
*client and admin*
returns json object with a specified user's location. This requires knowing the id of the user.
```json
{
    "location": {
        "city": "Chicago",
        "latitude": 41.833333333333336,
        "longitude": -87.68333333333334,
        "region": "USA",
        "timezone": "US/Central",
        "user_id": 22
    },
    "success": true
}
```
`GET '/users/{id}/events'`
returns json object with a specified user's events. This requires knowing the id of the user.
```json
{
    "success": true,
    "user": {
        "events": [
            {
                "busy": true,
                "description": "Let's see",
                "end_time": "2022-06-23T07:48:46.318560",
                "hour": 1,
                "id": 17,
                "planet": "Mars",
                "start_time": "2022-06-23T06:32:42.845341"
            }
        ],
        "id": 22,
        "location": {
            "city": "Chicago",
            "latitude": 41.833333333333336,
            "longitude": -87.68333333333334,
            "region": "USA",
            "timezone": "US/Central"
        },
        "username": "ahmed.jehairan@protonmail.com"
    }
}
```
`GET '/users/{id}/events'`
*client and admin*
returns json object with a specified user's events. This requires knowing the id of the user.
```json
{
    "success": true,
    "user": {
        "events": [
            {
                "busy": true,
                "description": "Let's see",
                "end_time": "2022-06-23T07:48:46.318560",
                "hour": 1,
                "id": 17,
                "planet": "Mars",
                "start_time": "2022-06-23T06:32:42.845341"
            }
        ],
        "id": 22,
        "location": {
            "city": "Chicago",
            "latitude": 41.833333333333336,
            "longitude": -87.68333333333334,
            "region": "USA",
            "timezone": "US/Central"
        },
        "username": "ahmed.jehairan@protonmail.com"
    }
}
```

`GET '/users/{id}/planetaryhours[?date=DATE]'`
returns json object with a specified user's planetary hours. This requires knowing the id of the user.
```json
{
    "planetary_hours": {
        "date": "2022-06-23T11:00:00",
        "planetaryhours": [
            [
                "Jupiter",
                [
                    "2022-06-23T05:16:39.372122",
                    "2022-06-23T06:32:42.845341"
                ]
            ],
            [
                "Mars",
                [
                    "2022-06-23T06:32:42.845341",
                    "2022-06-23T07:48:46.318560"
                ]
            ],
            [
                "Sun",
                [
                    "2022-06-23T07:48:46.318560",
                    "2022-06-23T09:04:49.791779"
                ]
            ],
            [
                "Venus",
                [
                    "2022-06-23T09:04:49.791779",
                    "2022-06-23T10:20:53.264998"
                ]
            ],
            [
                "Mercury",
                [
                    "2022-06-23T10:20:53.264998",
                    "2022-06-23T11:36:56.738217"
                ]
            ],
            [
                "Moon",
                [
                    "2022-06-23T11:36:56.738217",
                    "2022-06-23T12:53:00.211436"
                ]
            ],
            [
                "Saturn",
                [
                    "2022-06-23T12:53:00.211436",
                    "2022-06-23T14:09:03.684655"
                ]
            ],
            [
                "Jupiter",
                [
                    "2022-06-23T14:09:03.684655",
                    "2022-06-23T15:25:07.157874"
                ]
            ],
            [
                "Mars",
                [
                    "2022-06-23T15:25:07.157874",
                    "2022-06-23T16:41:10.631093"
                ]
            ],
            [
                "Sun",
                [
                    "2022-06-23T16:41:10.631093",
                    "2022-06-23T17:57:14.104312"
                ]
            ],
            [
                "Venus",
                [
                    "2022-06-23T17:57:14.104312",
                    "2022-06-23T19:13:17.577531"
                ]
            ],
            [
                "Mercury",
                [
                    "2022-06-23T19:13:17.577531",
                    "2022-06-23T20:29:21.050750"
                ]
            ],
            [
                "Sun",
                [
                    "2022-06-23T20:29:21.050750",
                    "2022-06-23T21:13:19.063336"
                ]
            ],
            [
                "Venus",
                [
                    "2022-06-23T21:13:19.063336",
                    "2022-06-23T21:57:17.075922"
                ]
            ],
            [
                "Mercury",
                [
                    "2022-06-23T21:57:17.075922",
                    "2022-06-23T22:41:15.088508"
                ]
            ],
            [
                "Moon",
                [
                    "2022-06-23T22:41:15.088508",
                    "2022-06-23T23:25:13.101094"
                ]
            ],
            [
                "Saturn",
                [
                    "2022-06-23T23:25:13.101094",
                    "2022-06-24T00:09:11.113680"
                ]
            ],
            [
                "Jupiter",
                [
                    "2022-06-24T00:09:11.113680",
                    "2022-06-24T00:53:09.126266"
                ]
            ],
            [
                "Mars",
                [
                    "2022-06-24T00:53:09.126266",
                    "2022-06-24T01:37:07.138852"
                ]
            ],
            [
                "Sun",
                [
                    "2022-06-24T01:37:07.138852",
                    "2022-06-24T02:21:05.151438"
                ]
            ],
            [
                "Venus",
                [
                    "2022-06-24T02:21:05.151438",
                    "2022-06-24T03:05:03.164024"
                ]
            ],
            [
                "Mercury",
                [
                    "2022-06-24T03:05:03.164024",
                    "2022-06-24T03:49:01.176610"
                ]
            ],
            [
                "Moon",
                [
                    "2022-06-24T03:49:01.176610",
                    "2022-06-24T04:32:59.189196"
                ]
            ],
            [
                "Saturn",
                [
                    "2022-06-24T04:32:59.189196",
                    "2022-06-24T05:16:57.201782"
                ]
            ]
        ],
        "yesterday": false
    },
    "success": true
}
```

`POST '/users/{id}/location'`
*client and admin*
stores location for specified user.
- Request Arguments:
  - user id
  - json body of either one of the following
    1. `{ "city" : city_name }`
    2. This:
```json
{
{
  "city": city name,
  "region": region name,
  "timezone": timezone compliant with pytz timezones (e.g. US/Central),
  "latitude":latitude decimal value (eg. 41.833333333333336),
  "longitude":longitude decimal value (eg. -87.68333333333334)
}}

```
- The api will look for the city in astral module database if user only passes city. If user passes the other data fields, the api will store given data after some logic checks.
- Returns
```json
{
  "location": {
    "city": "Chicago",
    "latitude": 41.833333333333336,
    "longitude": -87.68333333333334,
    "region": "USA",
    "timezone": "US/Central",
    "user_id": 22
  },
  "success": true
}
```

`PATCH '/users/{id}/events'`
*client and admin*
- patches an event to user's planner
- Request Arguments:
```json
{
    "hour": from 0 to 24, (required)
    "date" : "YYYY-MM-DD-HH:MM", (required)
    "description": "Let's see", (optional)
    "busy": boolean (default True)      
}
```
- Returns
```json
{
    "event": {
        "busy": true,
        "description": "Let's see",
        "end_time": "2022-06-23T07:48:46.318560",
        "hour": 1,
        "id": 17,
        "location_id": 25,
        "planet": "Mars",
        "start_time": "2022-06-23T06:32:42.845341",
        "user_id": 22
    },
    "success": true
}
```
`DELETE 'events/{id}'`
*client and admin*
- Deletes an event. Event id is required.
- Returns deleted event value 

`DELETE 'users/{id}'`
*admin only*
- Deletes a user. User id is required. *Cascades down to location and events.*
- Returns deleted user value


**Errors**
Examples of error messages:
No auth header:
```json
{
    "code": "authorization_header_missing",
    "description": "Authorization header is expected",
    "success": false
}
```
404:
```json
{
    "message": "Resource not found",
    "success": false
}
```

### Roles
- Admin: all permissions
- Client: no deleting or viewing all users