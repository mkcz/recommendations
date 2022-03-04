"""
Test cases for YourResourceModel Model

"""
from itertools import product
import logging
from math import prod
import unittest
import os
from service.models import ProductModel, DataValidationError, db
from service import app
from werkzeug.exceptions import NotFound

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  ProductModel   M O D E L   T E S T   C A S E S
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
        ProductModel.init_db(app)
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
        product = ProductModel(name="IPhone", category="phone")
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "IPhone")
        self.assertEqual(product.category, "phone")

    def test_add_a_product(self):
        """Create a item and add it to the database"""
        products = ProductModel.all()
        self.assertEqual(products, [])
        product = ProductModel(name="IPhone", category="phone")
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        product.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(product.id, 1)
        products = product.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """Update a item"""
        product = ProductModel(name="IPhone", category="phone")
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        product.create()
        # Change it an save it
        product.category = "laptop"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.category, "laptop")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = ProductModel.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, 1)
        self.assertEqual(products[0].category, "laptop")

    def test_update_a_product_validation_error(self):
        """Update a item Validation Error"""
        product = ProductModel(name="IPhone", category="Phone", id=None)
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """Delete a item"""
        product = ProductModel(name="IPhone", category="phone")
        product.create()
        self.assertEqual(len(product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(product.all()), 0)

    def test_serialize_a_product(self):
        """Test serialization of a item"""
        product = ProductModel(name="IPhone", category="phone")
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)

    def test_deserialize_a_product(self):
        """Test deserialization of a item"""
        data = {
            "name": "IPhone",
            "category": "phone"
        }
        product = ProductModel()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.name, "IPhone")
        self.assertEqual(product.category, "phone")

    def test_deserialize_missing_data(self):
        """Test deserialization of a item with missing data"""
        data = {"id": 1, "name": "Iphone"}
        product = ProductModel()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        product = ProductModel()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_find_product(self):
        """Find a product by ID"""
        products = productFactory.create_batch(3)
        for product in products:
            product.create()
        logging.debug(products)
        # make sure they got saved
        self.assertEqual(len(product.all()), 3)
        # find the 2nd product in the list
        product = product.find(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.category, products[1].category)
        self.assertEqual(product.price, products[1].price)

    def test_find_by_category(self):
        """Find items by Category"""
        product = ProductModel(name="IPhone", category="phone")
        product.create()
        product = ProductModel(name="Mac", category="Laptop")
        product.create()
        products = product.find_by_category("Laptop")
        self.assertEqual(products[0].category, "Laptop")
        self.assertEqual(products[0].name, "Mac")

    def test_find_by_name(self):
        """Find a item by Name"""
        product = ProductModel(name="IPhone", category="phone")
        product.create()
        product = ProductModel(name="Mac", category="Laptop")
        product.create()
        products = product.find_by_name("Mac")
        self.assertEqual(products[0].category, "Laptop")
        self.assertEqual(products[0].name, "Mac")

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        product = ProductModel(name="IPhone", category="phone",id=0)
        product.create()
        product = product.find_or_404(product.id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, product.id)
        self.assertEqual(product.name, product.name)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, ProductModel.find_or_404, 0)

    def test_find_products_of_same_category_greater_price(self):
        """Find products greater than the price of given item"""
        product = ProductModel(name="IPhone", category="phone",id=0, price=100)
        product.create()
        product = ProductModel(name="pixel", category="phone",id=1, price=200)
        product.create()
        products = product.find_products_of_same_category_greater_price("Iphone")
        self.assertIsNot(products, None)

    def test_find_products_of_same_category(self):
        """Find products of same category"""
        product = ProductModel(name="IPhone", category="phone",id=0, price=100)
        product.create()
        product = ProductModel(name="pixel", category="phone",id=0, price=200)
        product.create()
        products = product.find_products_of_same_category("Iphone")
        self.assertIsNot(products, None)

    def test_find_highest_price_product_by_category(self):
        """Find highest price product by category"""
        product = ProductModel(name="iPhone", category="phone",id=0, price=500)
        product.create()
        product = ProductModel(name="pixel", category="phone",id=1, price=200)
        product.create()
        product = ProductModel(name="samsung", category="phone",id=2, price=300)
        product.create()
        product = ProductModel(name="iMac", category="computer",id=3, price=1000)
        product.create()
        product = ProductModel.find_highest_price_product_by_category("phone")
        self.assertIsNot(product, None)
        self.assertEqual(product.name, "iPhone")
        self.assertEqual(product.category, "phone")
        self.assertEqual(product.id, 0)
        self.assertEqual(product.price, 500)
