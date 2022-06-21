"""Python Flask WebApp Auth0 integration example
"""

import json
import logging
import os
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, jsonify, request
from flask_cors import cross_origin, CORS

from auth import requires_auth, requires_scope
from autherror import AuthError
from flask_migrate import Migrate, MigrateCommand

from models import db, setup_db, Location, User

logging.basicConfig(level=env.get("LOGLEVEL", "INFO"), format='%(levelname)s - %(message)s')

# TODO Auth0 is set up and running at the time of submission. All required configuration settings are included in a
#  bash file which export:


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)
setup_db(app)
migrate = Migrate(app, db, compare_type=True)
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


# This doesn't need authentication
@app.route("/api/public")
def public():
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return jsonify(message=response)



# This needs authentication
@app.route("/api/private")
@requires_auth('read:planner')
def private(x):
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    # print(request.json)
    return jsonify({"test":response,
                    # "user":user
                    })
# @app.route("/api/users/user_id")
# @cross_origin(headers=["Content-Type", "Authorization"])
# def getuser():

# This needs authorization
@app.route("/api/private-scoped")
@requires_auth()
def private_scoped():
    if requires_scope("read:messages"):
        response = "Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this."
        return jsonify(message=response)
    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)


@app.route("/")
def home():
    user = session.get("user")
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )
@app.route("/users/<int:id>/settings",methods=["POST"])
def store_settings(id):
    print(id)
    user = session.get("user")
    result = request.form
    print(result.get('city'))
    location = Location(user_id=id,city=result.get('city',None),region=result.get('region',None),timezone=result.get('timezone','UTC')
                        ,latitude=float(result.get('latitude',0)),longitude=float(result.get('longitude',0)))
    location.insert()
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )



@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    print(token["userinfo"]["name"])
    user = User.query.filter_by(username=token["userinfo"]["name"]).one_or_none()
    if not user:
        user = User(username=token["userinfo"]["name"])
        user.insert()
        return render_template("settings.html",id=user.id)
    print(user)
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


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


if __name__ == "__main__":
    app.run(port=env.get("PORT", 3000))
    CORS(app, resources={r"/*": {"origins": "*"}})

