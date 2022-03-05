"""
Test cases for Product Model

"""
import os
import logging
import unittest
from service.models import Product, DataValidationError, db
from service import app
from werkzeug.exceptions import NotFound
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(unittest.TestCase):
    """ Test Cases for Product Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)
        pass

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()


    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """Create a item and assert that it exists"""
        product = Product(id=1, name="iPhone", category="phone", price=100)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "iPhone")
        self.assertEqual(product.category, "phone")
        self.assertEqual(product.price, 100)

    def test_add_a_product(self):
        """Create a item and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(id=1, name="iPhone", category="phone", price=100)
        self.assertTrue(product != None)
        self.assertEqual(product.id, 1)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = product.all()
        self.assertEqual(len(products), 1)
