# auth/routes.py

from flask import Blueprint, request, redirect, render_template
from utils.logger import secure_log

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
def login_page():
    return render_template("auth/login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    ip = request.remote_addr

    secure_log(f"Login attempt: {email} from {ip}")

    return redirect("/saml/login")
