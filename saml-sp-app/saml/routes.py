# saml/routes.py

from flask import Blueprint, request, redirect
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from utils.db import SessionLocal
from utils.models import AuthActivityLog

saml_bp = Blueprint("saml", __name__)

def prepare_flask_request(req):
    return {
        "https": "off", #temporary
        "http_host": req.host,
        "server_port": req.environ.get("SERVER_PORT"),
        "script_name": req.path,
        "get_data": req.args.copy(),
        "post_data": req.form.copy()
    }

@saml_bp.route("/saml/login")
def saml_login():
    auth = OneLogin_Saml2_Auth(prepare_flask_request(request))
    return redirect(auth.login())

@saml_bp.route("/saml/acs", methods=["POST"])
def saml_acs():
    auth = OneLogin_Saml2_Auth(prepare_flask_request(request))
    auth.process_response()
    return "SAML assertion received"

def log_auth_event(user_email, role, request, status):
    db = SessionLocal()
    db.add(AuthActivityLog(
        user_email=user_email,
        user_role=role,
        ip_address=request.remote_addr,
        auth_method="SAML",
        status=status,
        user_agent=request.headers.get("User-Agent")
    ))
    db.commit()
    db.close()
