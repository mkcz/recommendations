"""
Models for Product

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from flask import Flask


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Product(db.Model):
    """
    Class that represents a Product
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(63), nullable=False)
    category = db.Column(db.String(63), nullable=False)

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        if type(self.id) is not int:
            raise DataValidationError("Update called with non-integer ID field")
        if type(self.price) is not int:
            raise DataValidationError("Update called with non-integer price field")
        db.session.commit()

    def delete(self):
        """Removes a Pet from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Pet into a dictionary"""
        return {
            "id": self.id,
            "price": self.price,
            "name": self.name,
            "category": self.category,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Pet from a dictionary
        Args:
            data (dict): A dictionary containing the Pet data
        """
        try:
            self.name = data["name"]
            self.category = data["category"]
            if isinstance(data["price"], int):
                self.price = data["price"]
            else:
                raise DataValidationError(
                    "Invalid type for integer [price]:"
                    + str(type(data["price"]))
                )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid product: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data " + str(error)
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

