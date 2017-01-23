#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import synonym
from werkzeug.security import check_password_hash, generate_password_hash
from feederflask import db


class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    catname = db.Column(db.String(64), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)

    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, email, password):
        user = query(cls).filter(cls.email == email).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return '<User id={self.id} email={self.email!r}>'.format(self=self)


class Cataction(db.Model):
    __tablename__ = 'catactions'
    actionid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ownerid = db.Column(db.Integer, nullable=False)
    actiontime = db.Column(db.String(19), nullable=False)


    def __repr__(self):
        return '<actionid={self.actionid} owner={self.ownerid} actiontime={self.actiontime!r}>'.format(self=self)
    # ビューで代入したほうがよさそう...
    # def __init__(self, owner_id, action_time=None):
    #     self.owner_id = owner_id
    #     if action_time is None:
    #         action_time = (datetime.utcnow()+timedelta(hours=9)).strftime('%Y/%m/%d %H:%M:%S')
    #     self.action_time = action_time


# It contains feed waiting list
class Waiting(db.Model):
    __tablename__ = 'waitings'
    id = db.Column(db.Integer(), primary_key=True, nullable=False)

    def __repr__(self):
        return '<id={self.id!r}>'.format(self=self)


def init():
    db.create_all()