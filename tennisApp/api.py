from flask import request
from app import app, db, bcrypt, login_manager
from models import *
import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))