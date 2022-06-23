import os

from astral import LocationInfo
from pytz import timezone
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

from os import environ as env

import json
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

database_name = env.get('DATABASE_NAME')
database_path = env.get('DATABASE_URL')
# TODO Ask help about database optimization/setup ... whether my current set up makes sense
db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.drop_all()


"""
User

"""


class User(db.Model):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, unique=True, nullable=False)
    location = relationship("Location", back_populates="username", uselist=False)
    events = relationship("Events", back_populates="username")

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'username': self.username,
            'location': self.location.format_for_users(),
            'events': [event.format_for_users() for event in self.events],
        }


"""
Location

"""


class Location(db.Model):
    __tablename__ = 'Location'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    city = Column(String)
    region = Column(String)
    timezone = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    username = relationship("User", back_populates="location", uselist=False)
    events = relationship("Events",back_populates="location")

    def __init__(self, user_id, city, region, timezone, latitude, longitude):
        self.user_id = user_id
        self.city = city
        self.timezone = timezone
        self.region = region
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f'<Location {self.id}: ({self.user_id},{self.username}): {self.city}, {self.region}, {self.latitude}, {self.longitude}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def get_LocationInfo(self):
        return LocationInfo(self.city, self.region, self.timezone, self.latitude, self.longitude)
    def format(self):
        return {
            'user_id': self.user_id,
            'city': self.city,
            'timezone': self.timezone,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def format_for_users(self):
        return {
            'city': self.city,
            'timezone': self.timezone,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


"""
Events

"""


class Events(db.Model):
    __tablename__ = 'Events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    location_id = Column(Integer, ForeignKey(Location.id), nullable=False)
    # stored in UTC
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    description = Column(String)
    # when making new event, set time as busy
    busy = Column(Boolean, default=True)
    planet = Column(String, nullable=False)
    hour = Column(Integer,nullable=False)
    username = relationship("User", back_populates="events", uselist=False)
    location = relationship("Location", back_populates="events", uselist=False)

    def __init__(self, user_id, location_id,start_time,end_time, description, planet,hour,busy=True):
        self.user_id =  user_id
        self.location_id = location_id
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.busy = busy
        self.planet = planet
        self.hour= hour

    def __repr__(self):
        return f'<Event {self.id}: {self.start_time.replace(tzinfo=timezone(self.location.timezone))} to {self.end_time.replace(tzinfo=timezone(self.location.timezone))}({self.planet}),{self.description},{self.busy}>'

    def format_for_users(self):
        return {
            'id': self.id,
            'start_time': self.start_time.replace(tzinfo=timezone(self.location.timezone)),
            'end_time': self.end_time.replace(tzinfo=timezone(self.location.timezone)),
            'planet': self.planet,
            'description': self.description,
            'busy': self.busy,
            'hour':self.hour
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def format(self):
        return {
            'id': self.id,
            'user_id':self.user_id,
            'location_id':self.location_id,
            'start_time': self.start_time.replace(tzinfo=timezone(self.location.timezone)),
            'end_time': self.end_time.replace(tzinfo=timezone(self.location.timezone)),
            'planet': self.planet,
            'description': self.description,
            'busy': self.busy,
            'hour': self.hour
        }
