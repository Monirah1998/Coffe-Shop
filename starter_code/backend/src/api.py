from crypt import methods
import os
from sre_constants import SUCCESS
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES
@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message':'hello'}) 


@app.route('/drinks', methods= ['GET'])
def retrieve_drinks():
   try:
    return jsonify({
       "success": True,
       "drinks" : [drink.short() for drink in Drink.query.all()]
    }) ,200
   except:
       return jsonify({
            'success': False,
            'error': "ERROR !!! "
       })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_details(drink):
 try:
    Drink_Details = Drink.query.order_by(Drink.id).all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in Drink_Details]
    })
 except:
       return jsonify({
            'success': False,
            'error': "ERROR !!! "
       })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
  try:
    data = request.get_json()
    recipeDrink = json.dumps(data['recipe'])
    titleDrink = data['title']
    add_drink = Drink(title=titleDrink , recipe =recipeDrink)
    add_drink.insert()
    return jsonify({
        'success': True,
        'drinks': [add_drink.long()]
    })
  except:
    return jsonify({
            'success': False,
            'error': "ERROR !!! "
       })



@app.route('/drinks/<int:id>', methods=['PATCH'])
#require the 'patch:drinks' permission
@requires_auth('patch:drinks')
def update(drink, id):
 try:
    check_id = Drink.query.get(id)
    if check_id is None:
        abort(404)
    data = request.get_json()
    if 'title' in data: drink.title = data['title']

    if 'recipe' in data: drink.recipe = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

 except:
      return jsonify({
            'success': False,
            'error': "ERROR !!! "
       })


@app.route('/drinks/<int:id>', methods=['DELETE'])
#permission 
@requires_auth('delete:drinks')
#method delete drink 
def delete(drink, id):
    check_id = Drink.query.get(id)
    if check_id is None:
        abort(404)
    check_id.delete()
    
    return jsonify({
        'success': True,
        'delete': drink.id
    })




# Error Handling



@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error['description']
    }), e.status_code