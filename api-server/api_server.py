from flask import Flask, abort, jsonify, make_response, request
from flask_httpauth import HTTPTokenAuth
import sys

sys.path.insert(0, "./../");

from web_core.service import CoreService

app = Flask(__name__)
auth = HTTPTokenAuth()

svc = CoreService()

### APIs

@app.route("/webmovie/api/v0.1/guest")
def guest():
    """retrieve a list of avg-ranking movie list"""
    return "Hello World!"

@app.route('/webmovie/api/v0.1/signup', methods=["POST"])
def registeration():
    """get email,password(convert to passphrase) them save into db"""
    if not request.json or not 'email_address' in request.json:
        abort(400)
    elif not 'pass_code' in request.json:
        abort(400)
    rval = svc.register(request.json['email_address'], request.json['pass_code'])
    if rval >= 0:
        return make_response(jsonify({'user_id':rval}), 200)
    else:
        return make_response(jsonify({'error': 'Existing email address'}), 401)
   
@app.route('/webmovie/api/v0.1/signin', methods=["POST"])
def signin():
    """compare email, passphrase, then generate client_id:access_token"""
    return 'The about page, let get data from request'

@app.route("/webmovie/api/v0.1/recommend/<username>", methods=["GET"])
@auth.login_required
def recommend(username):
    return "User %s" %username

@app.route('/webmovie/api/v0.1/rated/<username>', methods=["GET"])
@auth.login_required
def rated(username):
    return 'User %s' %username

### Http error

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

### Authentication

@auth.verify_token
def verify(token):
    # this is client_id:access_token, verify it
    if token == "112288":
        return True
    return False

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

if __name__ == "__main__":
    if svc.start() == False:
        print "CoreService start fail"
    else:
        print "Movie CoreService started."
        app.run()
