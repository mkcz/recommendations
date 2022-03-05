"""
My Service

Describe what your service does here
"""

from itertools import product
from math import prod
import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound


# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import ProductModel, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="API to get recommendations for a item",
            version="1.0",
            paths=url_for("get_similar_products", _external=True),
        ),
        status.HTTP_200_OK,
    )

@app.route("/recommendations", methods=["GET"])
def get_similar_products():
    """Returns all of the recommendation"""
    app.logger.info("Request for recommendation for category")
    category = request.args.get("category")
    name = request.args.get("name")
    price = request.args.get("price")
    if category:
        products = ProductModel.find_by_category(category)
    elif name:
        products = ProductModel.find_products_of_same_category(name)
    elif price:
        products = ProductModel.find_products_of_same_category_greater_price(name)
    else:
        products = ProductModel.all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


@app.route("/recommendations/<int:item_id>", methods=["GET"])
def get_products(item_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request for product with id: %s", item_id)
    product = ProductModel.find(item_id)
    if not product:
        raise NotFound("Product with id '{}' was not found.".format(item_id))

    app.logger.info("Returning Information regarding product: %s", product.name)
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


@app.route("/recommendations", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to create a Product")
    check_content_type("application/json")
    product = ProductModel()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()
    location_url = url_for("get_products", item_id=product.id, _external=True)

    app.logger.info("product with ID [%s] created.", product.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


@app.route("/recommendations/<int:item_id>", methods=["PUT"])
def update_products(item_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to update a product with id: %s", item_id)
    check_content_type("application/json")
    product = ProductModel.find(item_id)
    if not product:
        raise NotFound("product with id '{}' was not found.".format(item_id))
    product.deserialize(request.get_json())
    product.id = item_id
    product.update()

    app.logger.info("product with ID [%s] updated.", product.id)
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


@app.route("/recommendations/<int:item_id>", methods=["DELETE"])
def delete_products(item_id):
    """
    Delete a Product

    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to delete product with id: %s", item_id)
    product = ProductModel.find(item_id)
    if product:
        product.delete()

    app.logger.info("product with ID [%s] delete complete.", item_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


@app.route("/recommendations/upsell/<string:category>", methods=["GET"])
def get_highest_price(category):
    """
    Retreive a single Product

    This endpoint will return a Product that is highest price in the category
    """
    app.logger.info("Request of product with highest price in the category: %s", category)
    product = ProductModel.find_highest_price_product_by_category(category)
    if not product:
        raise NotFound("No products is in the category '{}'.".format(category))

    app.logger.info("Returning Information regarding product: %s", product.name)
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )

def init_db():
    """ Initializes the SQLAlchemy app """
    ProductModel.init_db(app)