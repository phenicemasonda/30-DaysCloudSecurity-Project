from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from flask_session import Session
from datetime import datetime
import os
import psycopg2
import logging
from flask import make_response
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from saml.settings import saml_settings
from flask import request, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
# -------------------------
# App Configuration
# -------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "CHANGE_ME_IMMEDIATELY")


app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1
)


app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session") 
app.config["SESSION_FILE_THRESHOLD"] = 100 # optional, max sessions before cleanup
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True     # enforced behind ALB HTTPS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

Session(app)

# -------------------------
# Logging (placeholder – encryption next phase)
# -------------------------
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def init_saml_auth(req):
    with open('config/saml_settings.json') as f:
        saml_settings = json.load(f)

    return OneLogin_Saml2_Auth(req, saml_settings)

def prepare_flask_request(request):
    url_data = request.host_url
    return {
        "https": "on",
        "http_host": request.host,
        "server_port": request.environ.get("SERVER_PORT"),
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": request.form.copy(),
    }


# -------------------------
# Routes
# -------------------------



@app.route("/", methods=["GET"])
def index():
    """
    Render Landing Page first
    """
    return render_template("index.html")

@app.before_request
def enforce_https():
     if request.headers.get("X-Forwarded-Proto") != "https":
        return redirect(request.url.replace("http://", "https://"), code=301)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    show the Capture user input and initiate SAML login
    """
    if request.method == "GET": 
        return render_template("login.html")

    email = request.form.get("email")
    ip_address = request.remote_addr
    timestamp = datetime.utcnow().isoformat()

    if not email:
        return redirect(url_for("login"))

    # Store minimal session data
    session["user_email"] = email
    session["login_time"] = timestamp

    # Audit log (encrypted in later phase)
    logging.info(
        f"LOGIN_ATTEMPT email={email} ip={ip_address} time={timestamp}"
    )

    # Redirect to SAML login endpoint
    return redirect(url_for("saml_login"))


@app.route("/saml/login", methods=["GET"])
def saml_login():
    """
    Initiate SAML authentication
    (Redirect to AWS IAM Identity Center later)
    """
    if "user_email" not in session:
        return redirect(url_for("index"))

    # Placeholder for real SAML redirect
    logging.info(
        f"SAML_INIT email={session['user_email']}"
    )

    return (
        "<h2>SAML Login Initiated</h2>"
        "<p>Next step: Redirect to AWS IAM Identity Center</p>"
    )


@app.route("/logout", methods=["GET"])
def logout():
    """
    Clear session
    """
    session.clear()
    return redirect(url_for("index"))

@app.route("/saml/acs", methods=["POST"])
def saml_acs():
    req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(req, saml_settings())

    auth.process_response()

    errors = auth.get_errors()
    if errors:
        logging.error(f"SAML_ERRORS {errors}")
        return "SAML Authentication Failed", 401

    if not auth.is_authenticated():
        return "Unauthorized", 401

    attributes = auth.get_attributes()
    email = auth.get_nameid()

    session["user_email"] = email
    session["saml_attributes"] = attributes

    logging.info(
        f"SAML_SUCCESS email={email} attributes={attributes}"
    )

    return redirect("/dashboard")
@app.route("/saml/metadata", methods=["GET"])
def saml_metadata():
    settings = saml_settings()
    auth = OneLogin_Saml2_Auth({}, settings)
    metadata = auth.get_settings().get_sp_metadata()
    errors = auth.get_settings().validate_metadata(metadata)

    if errors:
        return make_response(", ".join(errors), 500)

    return make_response(metadata, 200, {"Content-Type": "text/xml"})



# -------------------------
# App Entrypoint
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
