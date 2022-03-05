"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db
from tests.factories import ProductFactory
from urllib.parse import quote_plus
#from unittest.mock import MagicMock, patch

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_products(self, count):
        """Factory method to create items in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            resp = self.app.post(
                BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = resp.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """Test the Home Page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "API to get recommendations for a item")

    def test_get_products_list(self):
        """Get a list of items"""
        self._create_products(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_product(self):
        """Get a single item"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        resp = self.app.get(
            "/recommendations/{}".format(test_product.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        """Get a product thats not found"""
        resp = self.app.get("/recommendations/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product(self):
        """Create a new product"""
        test_product = ProductFactory()
        logging.debug(test_product)
        resp = self.app.post(
            BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.name, "Names do not match")
        self.assertEqual(
            new_product["category"], test_product.category, "Categories do not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.name, "Names do not match")
        self.assertEqual(
            new_product["category"], test_product.category, "Categories do not match"
        )

    def test_create_product_no_data(self):
        """Create a item with missing data"""
        resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """Create a item with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product(self):
        """Update an existing item"""
        # create a product to update
        test_product = ProductFactory()
        resp = self.app.post(
            BASE_URL, json=test_product.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = resp.get_json()
        logging.debug(new_product)
        new_product["category"] = "unknown"
        resp = self.app.put(
            "/recommendations/{}".format(new_product["id"]),
            json=new_product,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["category"], "unknown")

    def test_delete_product(self):
        """Delete a item"""
        test_product = self._create_products(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_product.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_product.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_product_list_by_category(self):
        """Query items by Category"""
        products = self._create_products(10)
        test_category = products[0].category
        category_products = [product for product in products if product.category == test_category]
        resp = self.app.get(
            BASE_URL, query_string="category={}".format(quote_plus(test_category))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_get_highest_price(self):
        """Get the highest price product by category"""
        test_product = self._create_products(100)
        maxprice, category = 0, test_product[0].category
        for product in test_product:
            if product.category != category:
                continue
            maxprice = max(maxprice, product.price)
        resp = self.app.get(
            "/recommendations/upsell/{}".format(category),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        dataset = resp.get_json()
        for data in dataset:
            self.assertEqual(data["price"], maxprice)
            self.assertEqual(data["category"], category)

    def test_get_highest_price_not_found(self):
        """Get the highest price product by Category but not found"""
        resp = self.app.get("/recommendations/upsell/phone")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
