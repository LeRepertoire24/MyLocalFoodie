from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from config import Config

# Initialize the Blueprint
recipe_search = Blueprint('recipe_search', __name__)

# Database connection setup using environment variables
client = MongoClient(Config.MONGO_URI)
db = client[Config.MONGO_DBNAME]  # Using the MongoDB database name from config.py

def lookup_globalRecipe(db, globalRecipe_name):
    """
    Look up a recipe in the global_recipes collection using partial matches.
    """
    query = {'title': {'$regex': globalRecipe_name, '$options': 'i'}}
    return list(db[Config.COLLECTION_GLOBAL_RECIPES].find(query))

def lookup_userRecipe(db, userRecipe_name):
    """
    Look up a recipe in the user_recipes collection using partial matches.
    """
    query = {'title': {'$regex': userRecipe_name, '$options': 'i'}}
    return list(db[Config.COLLECTION_USER_RECIPES].find(query))

@recipe_search.route('/api/global_recipes', methods=['GET'])
def get_global_recipes():
    """
    Search for recipes in the global_recipes collection based on query parameters.
    """
    search_query = request.args.get('search_query', '')
    ingredient = request.args.get('ingredient', '')
    cuisine = request.args.get('cuisine', '')
    method = request.args.get('method', '')
    dietary = request.args.get('dietary', '')

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    query = {}

    if search_query:
        query["title"] = {"$regex": search_query, "$options": "i"}
    if ingredient:
        query["ingredients"] = {"$regex": ingredient, "$options": "i"}
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}
    if method:
        query["cookery_method"] = {"$regex": method, "$options": "i"}
    if dietary:
        query["dietary"] = {"$regex": dietary, "$options": "i"}

    try:
        recipes = db[Config.COLLECTION_GLOBAL_RECIPES].find(query).skip((page - 1) * limit).limit(limit)
        return dumps(list(recipes))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recipe_search.route('/api/user_recipes', methods=['GET'])
def get_user_recipes():
    """
    Search for recipes in the user_recipes collection based on query parameters.
    """
    search_query = request.args.get('search_query', '')
    ingredient = request.args.get('ingredient', '')
    cuisine = request.args.get('cuisine', '')
    method = request.args.get('method', '')
    dietary = request.args.get('dietary', '')

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    query = {}

    if search_query:
        query["title"] = {"$regex": search_query, "$options": "i"}
    if ingredient:
        query["ingredients"] = {"$regex": ingredient, "$options": "i"}
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}
    if method:
        query["cookery_method"] = {"$regex": method, "$options": "i"}
    if dietary:
        query["dietary"] = {"$regex": dietary, "$options": "i"}

    try:
        recipes = db[Config.COLLECTION_USER_RECIPES].find(query).skip((page - 1) * limit).limit(limit)
        return dumps(list(recipes))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
