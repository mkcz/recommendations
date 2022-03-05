"""
Recommendations Service

The recommendations resource is a representation a product recommendation based on another product
"""

from flask import jsonify, request, url_for, abort
from service.models import Recommendation
from . import app, status  # HTTP Status Codes

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendation REST API Service",
            version="1.0",
            paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################

@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    pass

######################################################################
# RETRIEVE A RECOMMENDATION BY ID
######################################################################


######################################################################
# ADD A NEW RECOMMENDATION
######################################################################


######################################################################
# UPDATE AN EXISTING RECOMMENDATION
######################################################################


######################################################################
# DELETE A RECOMMENDATION
######################################################################


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
    Recommendation.init_db(app)
