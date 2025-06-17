from flask import Flask, request, jsonify, redirect, render_template_string
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2 import OAuth2Error
from authlib.common.security import generate_token

app = Flask(__name__)
app.secret_key = 'ISCDEMO2025'

# In-memory "database"
users = {'alice': {'password': 'wonderland'}}
clients = {}
tokens = []

# Dummy client registration
clients['mysimpleclient'] = {
    'client_id': 'isc_client_id',
    'client_secret': 'fhiroauth_secret',
    'redirect_uris': ['http://localhost:3001/callback'],
    'scope': 'openid profile patient/*.read',
    'response_type': 'code',
    'grant_types': ['authorization_code'],
}

class User:
    def __init__(self, username):
        self.username = username

    def get_user_id(self):
        return self.username

def query_client(client_id):
    return clients.get(client_id)

def save_token(token, request):
    tokens.append(token)

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def authenticate_user(self, code):
        return User(code.user_id)

authorization = AuthorizationServer()
authorization.init_app(app, query_client=query_client, save_token=save_token)
authorization.register_grant(AuthorizationCodeGrant)

@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
    try:
        grant = authorization.get_consent_grant(end_user=User('alice'))
        if request.method == 'GET':
            return render_template_string('''
                <form method="post">
                    <h2>Authorize {{client.client_id}}?</h2>
                    <button type="submit" name="confirm" value="yes">Yes</button>
                </form>
            ''', client=grant.client)
        return authorization.create_authorization_response(grant_user=User('alice'))
    except OAuth2Error as e:
        return jsonify(dict(error=str(e)))

@app.route('/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()

@app.route('/userinfo')
def userinfo():
    return jsonify({
        "sub": "alice",
        "name": "Alice Example",
        "fhirUser": "Patient/alice"
    })

if __name__ == '__main__':
    app.run(debug=True, port=3000)
