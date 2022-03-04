"""
Models for YourResourceModel

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


class ProductModel(db.Model):
    """
    Class that represents a <your resource model name>
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    name = db.Column(db.String(63))
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
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid product: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data " + str(error)
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

    @classmethod
    def all(cls) -> list:
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, product_id: int):
        logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.get(product_id)

    @classmethod
    def find_or_404(cls, product_id: int):
        logger.info("Processing lookup or 404 for id %s ...", product_id)
        return cls.query.get_or_404(product_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
    
    @classmethod
    def find_products_of_same_category(cls, name: str):
        category = cls.query.filter(cls.name == name).first().category()
        return cls.query.filter(cls.category == category)
    
    @classmethod
    def find_products_of_same_category_greater_price(cls, item_name:str):
        price = cls.query.filter(cls.name == item_name).first()
        return cls.query.filter(cls.price > 100)


    @classmethod
    def find_by_category(cls, category: str) -> list:
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

