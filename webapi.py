import json
import requests

from utils import get_logger
from six.moves.urllib.request import urlopen
from monitor import Monitor
from datetime import timedelta
from functools import wraps, update_wrapper

from flask import Flask, request, jsonify, _request_ctx_stack, make_response, current_app
from flask_cors import CORS, cross_origin
from jose import jwt

AUTH0_DOMAIN = 'ar2ro.auth0.com'
API_AUDIENCE = 'https://api.arturonet.com'
ALGORITHMS = ["RS256"]

app = Flask(__name__)
# CORS(app)
logger = get_logger(__name__)
mon = Monitor()


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    logger.info(ex)
    return response

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def is_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        headers = { 'authorization': 'Bearer ' + token }
        r = requests.get('https://ar2ro.auth0.com/userinfo', headers=headers)
        r =r.json()
        if (('https://api.arturonet.com/roles' in r) and 'admin' in r['https://api.arturonet.com/roles']):
            return f(*args, **kwargs)
        else:
            raise AuthError({"code": "invalid_role",
                "description": "User is not an admin"}, 401)

    return decorated

def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience='https://api.arturonet.com',
                    issuer="https://ar2ro.auth0.com/",
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError as e:
                logger.info(e)
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated

@app.route('/')
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
@requires_auth
@is_admin
def index():
    raw = mon.check()
    json = {
        'error': raw[1],
        'running': raw[0]
    }
    return jsonify(json)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)

