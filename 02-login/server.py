"""Python Flask WebApp EPIC integration example
"""

import json
import requests
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, session, url_for
import sys

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
   
print("Python version:", sys.version)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

print(">>> server.py has started <<<")

FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"

oauth = OAuth(app)

oauth.register(
    "epic",
    client_id=env.get("EPIC_CLIENT_ID"),
    client_secret=env.get("EPIC_CLIENT_SECRET"),
    token_endpoint_auth_method="none",
    client_kwargs={
        "scope": "openid fhirUser user/patient.read",
    },
    server_metadata_url="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/.well-known/smart-configuration",
)


# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session,
        pretty=json.dumps(dict(session), indent=2),
        fhir_result=session.get("fhir_result"),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.epic.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    print("Redirect URI:", url_for("callback", _external=True))
    return oauth.epic.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/fhir-result")
def fhir_result():
    try:
        access_token = session["user"]["access_token"]
        headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/fhir+json",
         }
        response = requests.get(f"{FHIR_BASE_URL}/Patient/erXuFYUfucBZaryVksYEcMg3", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())  # Send JSON back to browser
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fhir")
def fhir():
    if "user" not in session:
        return redirect(url_for("home"))

    access_token = session["user"]["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/fhir+json",
    }

    try:
        response = requests.get(f"{FHIR_BASE_URL}/Patient/erXuFYUfucBZaryVksYEcMg3", headers=headers)
        fhir_json = response.json()
        response.raise_for_status()
        session["fhir_result"] = json.dumps(fhir_json, indent=2)
    except Exception as e:
        session["fhir_result"] = f"FHIR API error: {str(e)}"

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
