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

    def test_update_a_product(self):
        """Update a item"""
        product = Product(id=1, name="iPhone", category="phone", price=100)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, 1)
        product.create()
        # Change it an save it
        product.category = "laptop"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.category, "laptop")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, 1)
        self.assertEqual(products[0].category, "laptop")

    def test_update_a_product_validation_error(self):
        """Update a item Validation Error"""
        product = Product(id=1, name="iPhone", category="Phone", price="100")
        self.assertRaises(DataValidationError, product.update)
        product = Product(name="iPhone", category="Phone", price=100)
        self.assertRaises(DataValidationError, product.update)
        product = Product(id="1", name="iPhone", category="Phone", price=100)
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """Delete a item"""
        product = Product(id=1, name="iPhone", category="phone", price=100)
        product.create()
        self.assertEqual(len(product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(product.all()), 0)

    def test_serialize_a_product(self):
        """Test serialization of a item"""
        product = Product(name="iPhone", category="phone")
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
            "name": "iPhone",
            "category": "phone",
            "price": 500,
        }
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.name, "iPhone")
        self.assertEqual(product.category, "phone")
        self.assertEqual(product.price, 500)

    def test_deserialize_missing_data(self):
        """Test deserialization of a item with missing data"""
        data = {"id": 1, "name": "iPhone", "category": "phone"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        product = Product()
        data = "this is not a dictionary"
        self.assertRaises(DataValidationError, product.deserialize, data)
        data = {"id": 1, "name": "iPhone", "category": "phone", "price": "100"}
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_find_product(self):
        """Find a product by ID"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()
        logging.debug(products)
        # make sure they got saved
        self.assertEqual(len(Product.all()), 3)
        # find the 2nd product in the list
        product = product.find(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.category, products[1].category)
        self.assertEqual(product.price, products[1].price)

    def test_find_by_category(self):
        """Find products by Category"""
        Product(id=1, name="iPhone", category="phone", price=100).create()
        Product(id=2, name="Mac", category="laptop", price=500).create()
        products = Product.find_by_category("laptop")
        self.assertEqual(len(products.all()), 1)
        self.assertEqual(products[0].id, 2)
        self.assertEqual(products[0].category, "laptop")
        self.assertEqual(products[0].name, "Mac")
        self.assertEqual(products[0].price, 500)

    def test_find_by_name(self):
        """Find a product by Name"""
        Product(id=1, name="iPhone", category="phone", price=100).create()
        Product(id=2, name="Mac", category="laptop", price=500).create()
        products = Product.find_by_name("Mac")
        self.assertEqual(products[0].category, "laptop")
        self.assertEqual(products[0].name, "Mac")

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        Product(id=1, name="iPhone", category="phone", price=100).create()
        product = Product.find_or_404(1)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, product.id)
        self.assertEqual(product.name, product.name)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Product.find_or_404, 0)

    # def test_find_products_of_same_category_greater_price(self):
    #     """Find products greater than the price of given item"""
    #     Product(name="iPhone", category="phone", id=1, price=100).create()
    #     Product(name="pixel", category="phone", id=2, price=200).create()
    #     products = Product.find_products_of_same_category_greater_price("iPhone")
    #     self.assertIsNot(products, None)

    def test_find_products_of_same_category(self):
        """Find products of same category"""
        Product(name="iPhone", category="phone", id=1, price=100).create()
        Product(name="pixel", category="phone", id=2, price=200).create()
        products = Product.find_products_of_same_category("iPhone")
        self.assertIsNot(products, None)

    def test_find_highest_price_product_by_category(self):
        """Find highest price product by category"""
        Product(name="iPhone", category="phone",id=1, price=500).create()
        Product(name="pixel", category="phone",id=2, price=200).create()
        Product(name="galaxy", category="phone",id=3, price=500).create()
        Product(name="iMac", category="computer",id=4, price=1000).create()
        Product(name="oneplus", category="phone",id=5, price=400).create()
        products = Product.find_highest_price_product_by_category("phone")
        for product in products:
            self.assertEqual(product.category, "phone")
            self.assertEqual(product.price, 500)
