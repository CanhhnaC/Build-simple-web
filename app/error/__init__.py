from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.error import handlers