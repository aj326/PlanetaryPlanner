"""Python Flask WebApp Auth0 integration example
"""

import json
import logging
import os
from datetime import datetime, date
from os import environ as env
from urllib.parse import quote_plus, urlencode

import dateutil.parser
import pytz
import sqlalchemy
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, jsonify, request, abort
from flask.json import JSONEncoder
from flask_cors import cross_origin, CORS

from auth import requires_auth, requires_scope
from autherror import AuthError
from flask_migrate import Migrate, MigrateCommand

from models import db, setup_db, Location, User, Events
from planetaryhours import check_city, get_adjusted_hours, check_location

logging.basicConfig(level=env.get("LOGLEVEL", "INFO"), format='%(levelname)s - %(message)s')


# TODO Auth0 is set up and running at the time of submission. All required configuration settings are included in a
#  bash file which export:
class MyJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return super().default(o)


class MyFlask(Flask):
    json_encoder = MyJSONEncoder


app = MyFlask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)
setup_db(app)
migrate = Migrate(app, db, compare_type=True)
CORS(app, resources={r"/*": {"origins": "*"}})

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    # line below took ALOT OF DEBUGGING to reach!
    authorize_params={
        "audience": env.get("API_AUDIENCE")
    },
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# Controllers API
# Controllers API

# Format error response and append status code


@app.route("/")
def home():
    token = session.get("user",None)
    access_token = None
    if token:
        access_token=token['access_token']
        if not User.query.filter_by(username=token['userinfo']['name']).one_or_none():
            user = User(username=token['userinfo']['name'])
            user.insert()
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        access_token=access_token
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/users")
@requires_auth('read:users')
def get_users(permission):
    users = User.query.all()

    return jsonify({'success': True,
                    'users': [user.format() for user in users]
                    })


@app.route("/users/<int:id>/events")
@requires_auth('read:planner')
def get_events(permission, id):
    user = User.query.get(id)

    if user:
        return jsonify({'success': True,
                        'user': user.format(),
                        })
    else:
        abort(404, {'message': f"no user found with {id}"})


@app.route("/users/<int:id>/planetaryhours")
@requires_auth('read:planetaryhours')
def get_planetary_hours(permission, id):
    date = request.args.get('date', str(datetime.today()), type=str)

    location = Location.query.filter_by(user_id=id).one_or_none()
    if location:
        return jsonify({
            'success': True,
            'planetary_hours': get_adjusted_hours(location.get_LocationInfo(), dateutil.parser.parse(date))
        })
    else:
        abort(404, {'message': "no location found"})


@app.route("/users/<int:id>/location")
@requires_auth('read:location')
def get_location(permission, id):
    location = Location.query.filter_by(user_id=id).one_or_none()
    print(location)
    if location:
        return jsonify({'success': True,
                        'location': location.format()})
    else:
        abort(404, {'message': "no location found"})


@app.route("/users/<int:id>/location", methods=["POST"])
@requires_auth('post:location')
def store_location(permission, id):
    result = request.get_json()

    # print(result.get('city'))
    if not User.query.get(id):
        print("user not found")
        abort(404)
    location = Location.query.filter_by(user_id=id).all()
    print(location)
    if not location:
        # only passing city
        if (len(result.keys()) == 1 and result.get('city', None)):
            location = check_city(result.get('city'))
            if not location:
                print("city not found")
                abort(404, {'message': "city search returned no results, please pass full location JSON data"})
            else:
                location = Location(user_id=id, city=location.name, region=location.region, timezone=location.timezone
                                    , latitude=location.latitude, longitude=location.longitude)
        #passing all (necessary) data in JSON (Else to only city)
        else:
            if check_location(result.get('city', None), result.get('region', None),
                              result.get('timezone', "WRONG"), float(result.get('latitude', 0)),
                              float(result.get('longitude', 0))):
                location = Location(user_id=id, city=result.get('city', None), region=result.get('region', None),
                                    timezone=result.get('timezone', 'UTC')
                                    , latitude=float(result.get('latitude', 0)),
                                    longitude=float(result.get('longitude', 0)))
            else:
                abort(400)
        location.insert()
        return jsonify({'success': True,
                        'location': location.format()})
    # there is location already, todo CONSIDER changing it to 1-N relationship between user and locs
    else:
        abort(409)


#

@app.route("/users/<int:id>/events", methods=["POST"])
@requires_auth('post:event')
def post_event(permission, id):
    result = request.get_json()
    # print(result)
    if not User.query.get(id):
        abort(404, {'message': "no user found"})
    location = Location.query.filter_by(user_id=id).one_or_none()
    if not location:
        abort(404, {'message': "no location found"})
    hour = result.get('hour', None)
    date = result.get('date', None)
    description = result.get('description', None)
    busy = result.get('busy', True)
    if not date or not hour:
        abort(400, {'message': "date or hour missing"})
    if hour < 0 or hour > 24:
        abort(400, {'message': "hour out of bounds should be between [0,23]"})

    # TODO improve error handling here (do not allow location to be stored if it's not lligble
    try:
        hours = get_adjusted_hours(location.get_LocationInfo(), dateutil.parser.parse(date))
    except ValueError:
        abort(400,{'message': "sun astral"})

    event = Events(user_id=id, location_id=location.id, start_time=hours['planetaryhours'][hour][1][0],
                   end_time=hours['planetaryhours'][hour][1][1],
                   description=description, busy=busy,
                   planet=hours['planetaryhours'][hour][0], hour=hour)
    # print(event)
    try:
        event.insert()
    except sqlalchemy.exc.DataError:
        abort(500)
    # print(event)
    return jsonify({'success': True,
                    'event': event.format()})


@app.route("/events/<int:id>", methods=["PATCH"])
@requires_auth('patch:event')
def patch_event(permission, id):
    response = request.get_json()
    print(response)
    event = Events.query.get(id)

    if not event:
        abort(404, {'message': "no event found"})
    hour = response.get('hour', None)
    date = response.get('date', None)
    description = response.get('description', None)
    busy = response.get('busy', None)
    if hour < 0 or hour > 24:
        abort(400, {'message': "hour out of bounds should be between [0,23]"})
    if date and hour:
        hours = get_adjusted_hours(event.location.get_LocationInfo(), dateutil.parser.parse(date))
        event.start_time = hours['planetaryhours'][hour][1][0]
        event.start_time = hours['planetaryhours'][hour][1][1]
        event.planet = hours['planetaryhours'][hour][0]
        event.hour = hour
    if not date and hour:
        hours = get_adjusted_hours(event.location.get_LocationInfo(), event.start_time)
        event.start_time = hours['planetaryhours'][hour][1][0]
        event.start_time = hours['planetaryhours'][hour][1][1]
        event.planet = hours['planetaryhours'][hour][0]
        event.hour = hour
    if description:
        event.description = description
    if busy is not None:
        event.busy = busy
    try:
        event.update()
    except sqlalchemy.exc.DataError:
        abort(500)
    # print(event)
    return jsonify({'success': True,
                    'event': event.format()})


@app.route("/users/<int:id>", methods=['DELETE'])
@requires_auth('delete:user')
def delete_user(permission, id):
    user = User.query.get(id)
    if user:
        user_val = user.format()
        user.delete()
        user_val['success'] = True
        return jsonify(user_val)
    else:
        abort(404)


@app.route("/events/<int:id>", methods=["DELETE"])
@requires_auth('delete:event')
def delete_event(permission, id):
    event = Events.query.get(id)
    if event:
        event_val = event.format()
        event_val['success'] = True
        event.delete()
        return jsonify(event_val)
    else:
        abort(404)


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    ex.error['success'] = False
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(400)
def bed_request_error(e):
    return jsonify({'success': False,
                    'message': f"Bad request"}), 400



@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'success': False,
                    'message': f"Resource not found"}), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False,
                    'message': f"Internal server error"}), 500


@app.errorhandler(409)
def conflict_error(e):
    return jsonify({'success': False,
                    'message': f"Conflict"}), 409


if __name__ == "__main__":
    app.run(port=env.get("PORT", 3000))
