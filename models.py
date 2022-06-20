import os
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

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    location = relationship("Location", back_populates="user", uselist=False)
    events = relationship("Events",back_populates="user")

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return f'<User {self.id}: {self.username}'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


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


    def __init__(self, user_id, city,region,timezone,latitude, longitude):
        self.user_id = user_id
        self.city = city
        self.timezone = timezone
        self.region = region
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f'<Location {self.id}: ({self.user_id},{self.username}): {self.city}, {self.region}, {self.latitude}, {self.longitude}'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


"""
Events

"""

class Events(db.Model):
    __tablename__ = 'Events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    location_id =  Column(Integer, ForeignKey(Location.id), nullable=False)
    # stored in UTC
    time = Column(DateTime, unique=True, nullable=False)
    description=Column(String)
    #when making new event, set time as busy
    busy = Column(Boolean,default=True)
    username = relationship("User", back_populates="events", uselist=False)

    def __init__(self, time,description,busy):
        self.time = time
        self.description = description
        self.busy = busy

    def __repr__(self):
        return f'<Event {self.id}: {self.time},{self.description},{self.busy}'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()