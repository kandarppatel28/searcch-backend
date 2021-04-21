from searcch_backend.api.app import app
from searcch_backend.api.app import db
from searcch_backend.models.model import *
from datetime import datetime
from flask import abort


def verify_api_key(api_key, config_name):
    if api_key == '':
        abort(403, description="missing secret api key")
    if config_name == 'development' and api_key != app.config.get('SHARED_SECRET_KEY'):
        abort(401, description="dev: incorrect secret api key")
    if config_name == 'production' and api_key != app.config.get('SHARED_SECRET_PROD_KEY'):
        abort(401, description="prod: incorrect secret api key")


def verify_token(sso_token):
    # sanity check input
    if sso_token == '':
        abort(403, description="missing SSO token from auth provider")

    # check for token in sessions table
    login_session = db.session.query(Sessions).filter(Sessions.sso_token == sso_token).first()
    if login_session:
        if login_session.expires_on < datetime.now():  # token has expired
            # delete token from sessions table
            db.session.delete(login_session)
            db.session.commit()

            # send back for relogin
            abort(401, description="session token has expired. please re-login")
        else:
            return True
    else:
        return False
