import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# !! Running this funciton will add one

# db_drop_and_create_all()

# ROUTES
# '''
# @TODO implement endpoint
#     GET /drinks
#         it should be a public endpoint
#         it should contain only the drink.short() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''

# this endpoint is a public one and it returns a list of available drinks
@app.route('/drinks')
def get_drinks():
    selection = Drink.query.order_by(Drink.id).all()

    if len(selection) == 0:
        abort(404)
    
    drinks = [drink.short() for drink in selection]

    # returns a short form data representation of drinks
    return jsonify({
        "success": True,
        "drinks" : drinks
    })


# '''
# @TODO implement endpoint
#     GET /drinks-detail
#         it should require the 'get:drinks-detail' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''

# this enpoint requires a permission, so not everyone should get access on it
# the endpoint retrieves a list of drinks in a long form
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    selection = Drink.query.order_by(Drink.id).all()

    if len(selection) == 0:
        abort(404)
    
    drinks = [drink.long() for drink in selection]

    # returns a long form data representation of drinks
    return jsonify({
        "success": True,
        "drinks" : drinks
    })


# '''
# @TODO implement endpoint
#     POST /drinks
#         it should create a new row in the drinks table
#         it should require the 'post:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
#         or appropriate status code indicating reason for failure
# '''

# this endpoint requres a post permission, so not everyone should get access on it
# the enpoint creates a new row in the drinks table then returns it back
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks():
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            "success": True,
            "drinks" : [drink.long()]
        })
    except:
        abort(422)


# '''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''

# this endpoint requires a patch permission, so not everyone should get access on it
# the enpoint updates a specific row in the drinks table then returns it back
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(drink_id):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        
        drink.title = title
        drink.recipe = recipe
        drink.update()

        return jsonify({
            "success": True,
            "drinks" : [drink.long()]
        })
    except:
        abort(422)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
# this endpoint requires a delete permission, so not everyone should get access on it
# the enpoint delete a specific row in the drinks table then returns back his id
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(drink_id):
       
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except:
        abort(422)


# ERROR HANDLING

# the resource not found error handler
@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404,
                "message": "Resource not found"}),
        404,
    )

# the unprocessable error handler
@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422,
                "message": "Unprocessable"}),
        422,
    )


    return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

# the method not allowed error handler
@app.errorhandler(405)
def method_not_allowed(error):
    return (
        jsonify({"success": False, "error": 405,
                "message": "Method not allowed"}),
        405,
    )


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

# this link helped me out...
# https://stackoverflow.com/questions/53285452/internal-server-error-rather-than-raised-autherror-response-from-auth0

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.exception)
    response.status_code = ex.status_code
    return response
