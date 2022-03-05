"""
Models for Recommendations

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Type(Enum):
    """Enumeration of valid Recommendation Types"""

    CROSS_SELL = 0
    UP_SELL = 1
    ACCESSORY = 2


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True) # recommendation id
    src_product_id = db.Column(db.Integer, nullable=False) # source product id
    rec_product_id = db.Column(db.Integer, nullable=False) # recommended product id
    type = db.Column( # recommendation type
        db.Enum(Type), nullable=False, server_default=(Type.CROSS_SELL.name)
    )

    def __repr__(self):
        return "<Recommendation id=[%s], src_product_id=[%s], rec_product_id=[%s], type=[%s]>" % \
            (self.id, self.src_product_id, self.rec_product_id, self.type.name)

    def serialize(self) -> dict:
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "src_product_id": self.src_product_id,
            "rec_product_id": self.rec_product_id,
            "type": self.type.name, # convert enum to string
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Recommendation from a dictionary
        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        try:
            self.src_product_id = data["src_product_id"]
            self.rec_product_id = data["rec_product_id"]
            self.type = getattr(Type, data["type"])  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid recommendation: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid recommendation: body of request contained bad or no data " + str(error)
            )
        return self

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session
        :param app: the Flask app
        :type data: Flask
        """
        logger.info("Initializing database")
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
