from flask import Flask, abort, jsonify, make_response, request
from flask_httpauth import HTTPTokenAuth
import sys

sys.path.insert(0, "./../");

from web_core.service import CoreService

app = Flask(__name__)
auth = HTTPTokenAuth()

svc = CoreService()

### Constants
_EMAIL_KEY = "email_address"
_PW_KEY = "password"
_USER_ID_KEY = "user_id"
_ERROR_KEY = "error"
_STATUS__KEY = 'status'
_TOKEN_KEY = "access_token"

_MOVIE_ID_KEY = 'movie_id'
_RATING_KEY = 'rating'
### APIs

@app.route("/webmovie/api/v0.1/guest")
def guest():
    """retrieve a list of avg-ranking movie list"""
    begin = request.args.get('begin')
    end = request.args.get('end')
    ### need sanity check on arguments
    movie_list = svc.avg_ranking(int(begin), int(end))
    return make_response(jsonify({'movie_list': movie_list}), 200)

@app.route('/webmovie/api/v0.1/signup', methods=["POST"])
def registeration():
    """get email,password(convert to passphrase) them save into db"""
    if not request.json or not _EMAIL_KEY in request.json:
        abort(400)
    elif not _PW_KEY in request.json:
        abort(400)

    user_id, access_token = svc.register(request.json[_EMAIL_KEY], request.json[_PW_KEY])
    if user_id >= 0:
        return make_response(jsonify({_USER_ID_KEY: user_id, _TOKEN_KEY: access_token}), 200)
    else:
        return make_response(jsonify({_ERROR_KEY: 'Existing email address'}), 401)
   
@app.route('/webmovie/api/v0.1/signin', methods=["POST"])
def signin():
    """compare email, passphrase, then generate client_id:access_token"""
    if not request.json or not _EMAIL_KEY in request.json:
        abort(400)
    elif not _PW_KEY in request.json:
        abort(400)
    user_id, access_token = svc.auth(request.json[_EMAIL_KEY], request.json[_PW_KEY])
    if user_id >= 0:
        return make_response(jsonify({_USER_ID_KEY: user_id, _TOKEN_KEY: access_token}), 200)
    else:
        return make_response(jsonify({_ERROR_KEY: 'Authentication fail'}), 401)

@app.route("/webmovie/api/v0.1/recommend/<int:user_id>", methods=["GET"])
@auth.login_required
def recommend(user_id):
    begin = request.args.get('begin')
    end = request.args.get('end')
    return "user %d\n" %user_id

@app.route('/webmovie/api/v0.1/rated/<int:user_id>', methods=["GET"])
@auth.login_required
def rated(user_id):
    begin = request.args.get('begin')
    end = request.args.get('end')
    return 'User %d\n' %user_id

@app.route('/webmovie/api/v0.1/add_rating/<int:user_id>', methods=["POST"])
@auth.login_required
def add_rating(user_id):
    if not request.json or (not _MOVIE_ID_KEY in request.json
                            or not _RATING_KEY in request.json):
        abort(400)
    movie_id = request.json[_MOVIE_ID_KEY]
    rating = request.json[_RATING_KEY]
    if svc.add_rating(user_id, movie_id, rating) == True:
        return make_response(jsonify({_STATUS__KEY: 'success'}), 200)
    else:
        return make_response(jsonify({_ERROR_KEY: 'fail'}), 401)

### Http error

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({_ERROR_KEY: 'Not found'}), 404)

### Authentication

@auth.verify_token
def verify(token):
    # verify api/v0.1/xxx/<user_id> and access_token
    user_id = int(request.path.split('/')[-1])
    return svc.verify_token(user_id, token)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({_ERROR_KEY: 'Unauthorized access'}), 401)

if __name__ == "__main__":
    if svc.start(sys.argv[1]) == False:
        print "CoreService start fail"
    else:
        print "Movie CoreService started."
        app.run()
