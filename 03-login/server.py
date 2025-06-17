"""Python Flask WebApp FHIR integration example
"""

import json
import requests
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, session, url_for
import sys
import logging


logging.basicConfig(level=logging.DEBUG)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

print("Here is the client id=" + env.get("AUTH0_CLIENT_ID"))
    
   
print("Python version:", sys.version)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

print(">>> server.py has started <<<")

FHIR_BASE_URL = "https://localhost:8443/csp/healthshare/demo/fhir/r4/"

oauth = OAuth(app)

oauth.register(
    'auth0',
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
    api_base_url=f'https://{env.get("AUTH0_DOMAIN")}',
    access_token_url=f'https://{env.get("AUTH0_DOMAIN")}/oauth/token',
    authorize_url=f'https://{env.get("AUTH0_DOMAIN")}/authorize',
    client_kwargs={
        'scope': 'user/*.*',
    },
)


# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session,
        pretty=json.dumps(dict(session), indent=2),
        fhir_result=None,
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token(withhold_id_token=True)
    print(json.dumps(token, indent=2))
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    session.clear()
    print("Redirect URI:", url_for("callback", _external=True))
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        audience="https://localhost:8443/csp/healthshare/demo/fhir/r4"
    )


@app.route("/fhir-result")
def fhir_result():
    try:
        access_token = session["user"]["access_token"]
        headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/fhir+json",
         }
        response = requests.get(f"{FHIR_BASE_URL}/Patient/2", headers=headers, verify="intersystems.crt")
        response.raise_for_status()
        return jsonify(response.json())  # Send JSON back to browser
    except Exception as e:
        print(jsonify({"error": str(e)}))
        return jsonify({"error": str(e)}), 500


@app.route("/fhir")
def fhir():
    if "user" not in session:
        return redirect(url_for("home"))

    access_token = session["user"]["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/fhir+json",
        "content-type": "application/fhir+json",
        "Accept-Encoding": "gzip, deflate, br",
        "Prefer": "return=representation"
    }

    try:
        response = requests.get(f"{FHIR_BASE_URL}/Patient/2", headers=headers)
        fhir_json = response.json()
        response.raise_for_status()
        session["fhir_result"] = json.dumps(fhir_json, indent=2)
    except Exception as e:
        session["fhir_result"] = f"FHIR API error: {str(e)}"

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
