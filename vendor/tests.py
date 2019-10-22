import os
import json
import unittest

from django.test import TestCase, Client, RequestFactory
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from vendor.models import Offer, Price, Invoice, OrderItem, Purchases
from core.models import Product


class DataTestMixin(object):
    '''
    Check the response data against validation JSON file
    '''

    def load_data(self, path=None):
        path_parts = path.split('/')
        check_data_file = os.path.join(settings.BASE_DIR, *path_parts)
        check_data = json.loads(open(check_data_file, 'r').read())
        return check_data

    def uri_check_against_data(self, client, target_uri, validation_data, method="get", response_code=200):
        '''
        Make sure the response is the expected data.
        '''
        try:
            response = getattr(client, method)(target_uri)
            content = json.loads(response.content)
            self.assertEqual(response.status_code, response_code)     # 200 -> Return Response Code
            self.assertEqual(validation_data, content)
        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(response.data)
            raise

        return validation_data, response

    def uri_check_keys(self, client, target_uri, validation_data, method="get", response_code=201, **kwargs):
        '''
        Make sure the response has the same keys as the expected data.
        '''

        try:
            response = getattr(client, method)(target_uri, data=kwargs)
            self.assertEqual(response.status_code, response_code)     # 201 -> Created Response Code
            self.assertEqual(response.data.keys(), validation_data.keys())
        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(response.data)
            raise

        return response

    def uri_check_deleted(self, client, delete_uri, retrieve_uri):
        '''
        Make sure a given uri deletes the resource
        '''

        try:
            response = self.client.delete(delete_uri)
            self.assertEqual(response.status_code, 204)     # 204 -> Return Response Code
        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(delete_uri)
            print(response.data)
            raise

        # Confirm it is deleted...
        try:
            response = self.client.get(retrieve_uri)
            self.assertEqual(response.status_code, 404)     # 404 -> Return Response Code
        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(retrieve_uri)
            print(response.data)
            raise


##################
# View Level Tests
##################

# class FactoryTests(TestCase):
#     factory = RequestFactory()
#
#     #TestCases for CART
#
#     def test_add_to_cart(self):
#         request = self.factory.post('/add-to-cart/1J0RO6LH/', data={})
#         self.assertEqual(request.method, "POST")
#
#
#     def test_retreive_cart(self):
#         request = self.factory.get('/retrieve-cart/1J0RO6LH/')
#         assert(request.content_type == "application/octet-stream")
#         assert(request.method == "GET")
#
#
#     def test_remove_item_from_cart(self):
#         request = self.factory.put('/remove-item-from-cart/1J0RO6LH/', data={})
#         self.assertEqual(request.method, "PUT")
#
#     def test_remove_single_item_from_cart(self):
#         request = self.factory.put('/remove-single-item-from-cart/1J0RO6LH/', data={})
#         self.assertEqual(request.method, "PUT")
#
#
#     def test_delete_cart(self):
#         request = self.factory.delete('/delete-cart/1J0RO6LH/')
#         assert(request.method == "DELETE")


###################
# CART CLIENT TEST
###################

##############
# ADD TO CART
##############

class AddToCartClientTest(TestCase):
    '''
    Tests for AddToCart Functionality
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')
        self.product = Product.objects.create(name = "Test Product")

    def test_add_to_cart_create_invoice(self):
        '''
        Test for adding item to the cart when there is no invoice for the user with cart status.
        '''
        self.client.force_login(self.user)

        offer = Offer.objects.create(product = self.product)
        invoice = Invoice.objects.filter(user = self.user, status = 0).count()

        uri = reverse('vendor-add-to-cart-api', kwargs={'sku': offer.sku})
        response = self.client.post(uri)

        new_invoice = Invoice.objects.filter(user = self.user, status = 0).count()
        orderitem = OrderItem.objects.filter(offer = offer).count()

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Created Response Code
            self.assertEqual(invoice, 0)
            self.assertEqual(new_invoice, 1)
            self.assertEqual(orderitem, 1)

        except:
            print("")
            print(response.data)
            raise


    def test_add_to_cart_create_order_item(self):
        '''
        Test for adding item to the cart
        '''
        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product)
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())
        orderitem = OrderItem.objects.filter(offer = offer, invoice = invoice).count()

        uri = reverse('vendor-add-to-cart-api', kwargs={'sku': offer.sku})
        response = self.client.post(uri)

        new_orderitem = OrderItem.objects.filter(offer = offer, invoice = invoice).count()

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Created Response Code
            self.assertEqual(orderitem, 0)
            self.assertEqual(new_orderitem, 1)

        except:
            print("")
            print(response.data)
            raise


    def test_add_to_cart_increment_offer_quantity(self):
        '''
        Test for adding item to the cart which is already in the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        price = offer.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())
        orderitem = OrderItem.objects.create(invoice = invoice, offer = offer, price = price)

        uri = reverse('vendor-add-to-cart-api', kwargs={'sku': offer.sku})
        response = self.client.post(uri)

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Created Response Code
            self.assertEqual(orderitem.quantity, 1)
            self.assertGreater(OrderItem.objects.get(offer = offer, invoice = invoice).quantity, 1)

        except:
            print("")
            print(response.data)
            raise

###################
# DELETE FROM CART
###################

class RemoveItemFromCartClientTest(TestCase):
    '''
    Tests for Cart Functionality
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')
        self.product = Product.objects.create(name = "Test Product")

    def test_remove_item_from_cart(self):
        '''
        Test for removing the item from the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        price = offer.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())
        orderitem = OrderItem.objects.create(invoice = invoice, offer = offer, price = price)

        uri = reverse('remove-from-cart-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        order = OrderItem.objects.filter(offer = offer, invoice = invoice).count()

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Created Response Code
            self.assertEqual(order, 0)

        except:
            print("")
            print(response.data)
            raise


    def test_remove_item_from_cart_fail_1(self):
        '''
        Test for removing the item not present in the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())

        uri = reverse('remove-from-cart-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 404)     # 404 -> Created Response Code

        except:
            print("")
            print(response.data)
            raise


    def test_remove_item_from_cart_fail_2(self):
        '''
        Test for removing the item from the cart with no active cart for the user
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)

        uri = reverse('remove-from-cart-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 400)     # 404 -> Created Response Code

        except:
            print("")
            print(response.data)
            raise


##################################
# DECREASE ITEM QUANTITY IN CART
##################################

class DecreaseItemQuantityClientTest(TestCase):
    '''
    Tests for Cart Functionality
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')
        self.product = Product.objects.create(name = "Test Product")

    def test_decrease_quantity_from_cart(self):
        '''
        Test for decreasing the quantity of the item already in the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        price = offer.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())
        orderitem = OrderItem.objects.create(invoice = invoice, offer = offer, price = price)

        increase_item_quantity_uri = reverse('vendor-add-to-cart-api', kwargs={'sku': offer.sku})
        cart_response = self.client.post(increase_item_quantity_uri)

        quantity = OrderItem.objects.get(offer = offer, invoice = invoice).quantity

        uri = reverse('remove-single-item-from-cart-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Created Response Code
            self.assertEqual(quantity, 2)
            self.assertLess(OrderItem.objects.get(offer = offer, invoice = invoice).quantity, quantity)

        except:
            print("")
            print(response.data)
            raise


    def test_decrease_quantity_from_cart_fail_1(self):
        '''
        Test for decreasing the quantity of the item when there is no active cart for the user
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)

        uri = reverse('remove-single-item-from-cart-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 400)     # 400 -> Created Response Code

        except:
            print("")
            print(response.data)
            raise


    def test_decrease_quantity_from_cart_fail_2(self):
        '''
        Test for decreasing the quantity of the item not present in the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())

        uri = reverse('remove-single-item-from-cart-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 404)     # 404 -> Created Response Code

        except:
            print("")
            print(response.data)
            raise


##################################
# INCREASE ITEM QUANTITY IN CART
##################################

class IncreaseItemQuantityTest(TestCase):
    '''
    Tests for Cart Functionality
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')
        self.product = Product.objects.create(name = "Test Product")

    def test_increase_item_quantity(self):
        '''
        Test for increasing the quantity of an item in the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        price = offer.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())
        orderitem = OrderItem.objects.create(invoice = invoice, offer = offer, price = price)

        quantity = OrderItem.objects.get(offer = offer, invoice = invoice).quantity

        uri = reverse('increase-item-quantity-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        updated_quantity = OrderItem.objects.get(offer = offer, invoice = invoice).quantity

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Created Response Code
            self.assertGreater(updated_quantity, quantity)

        except:
            print("")
            print(response.data)
            raise

    def test_increase_item_quantity_fail_1(self):
        '''
        Test for increasing the quantity of the item when there is no active cart for the user
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)

        uri = reverse('increase-item-quantity-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 400)     # 400 -> Created Response Code

        except:
            print("")
            print(response.data)
            raise


    def test_increase_item_quantity_fail_2(self):
        '''
        Test for increasing the quantity of the item not present in the cart
        '''

        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())

        uri = reverse('increase-item-quantity-api', kwargs={'sku': offer.sku})
        response = self.client.patch(uri)

        try:
            self.assertEqual(response.status_code, 404)     # 404 -> Created Response Code

        except:
            print("")
            print(response.data)
            raise


#################
# RETRIEVE CART
#################

class RetrieveCartClientTest(DataTestMixin, TestCase):
    '''
    Tests for Cart Functionality
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')
        self.product = Product.objects.create(name = "Test Product")
        self.product2 = Product.objects.create(name = "Test Product2")

    def test_cart_retrieve(self):
        '''
        Test for retrieving a cart for the user
        '''

        self.client.force_login(self.user)

        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)
        price = offer.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()

        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())

        orderitem = OrderItem.objects.create(invoice = invoice, offer = offer, price = price)

        offer2 = Offer.objects.create(product = self.product2, name = self.product2.name, msrp = 90.0)
        price2 = offer2.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()

        orderitem2 = OrderItem.objects.create(invoice = invoice, offer = offer2, price = price2, quantity = 2)

        check_data = {
              "username": "testuser",
              "order_items": [
                {
                  "sku": "MWSHDGQN",
                  "name": "Test Product",
                  "price": "50.00",
                  "item_total": "50.00",
                  "quantity": 1
                },
                {
                  "sku": "MWSHDGQN",
                  "name": "Test Product2",
                  "price": "90.00",
                  "item_total": "180.00",
                  "quantity": 1
                }
              ],
              "total": "230.00"
            }

        uri = reverse('vendor-user-cart-retrieve-api')
        response = self.client.get(uri)

        try:
            self.assertEqual(response.status_code, 200)     # 200 -> Return Response Code
            self.assertEqual(response.data.keys(), check_data.keys())
            self.assertEqual(response.data["order_items"][0].keys(), check_data["order_items"][0].keys())

        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(response)
            print(response.data)
            raise


    def test_cart_retrieve_fail(self):
        self.client.force_login(self.user)
        offer = Offer.objects.create(product = self.product, name = self.product.name, msrp = 50.0)

        uri = reverse('vendor-user-cart-retrieve-api')
        response = self.client.get(uri)

        try:
            self.assertEqual(response.status_code, 404)     # 404 -> Return Response Code

        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(response)
            raise


###################
# OFFER MODEL TEST
###################

class OfferModelTest(TestCase):
    '''
    Test for Offer Model Test
    '''

    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name = "Test Product")


    def test_price_object_created(self):

        offer = Offer.objects.create(product=self.product, msrp = 80)
        price_object_count = offer.sale_price.all().count()

        try:
            self.assertEqual(price_object_count, 1)

        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(offer)
            raise


    def test_current_price(self):

        offer = Offer.objects.create(product=self.product, msrp = 80)
        price = Price.objects.create(offer = offer, cost = 90, priority=2, start_date = timezone.now(), end_date = timezone.now() + timezone.timedelta(days=1))

        try:
            self.assertEqual(offer.current_price(), offer.sale_price.all()[0].cost)

        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(offer)
            print(offer.current_price())
            raise


###################
# PRICE MODEL TEST
###################

class PriceModelTest(TestCase):
    '''
    Test for Price Model Test
    '''

    def setUp(self):
        pass


#####################
# INVOICE MODEL TEST
#####################

class InvoiceModelTest(TestCase):
    '''
    Test for Invoice Model Test
    '''

    def setUp(self):
        pass


#######################
# ORDERITEM MODEL TEST
#######################

class OrderItemModelTest(TestCase):
    '''
    Test for OrderItem Model Test
    '''

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')
        self.product = Product.objects.create(name = "Test Product")

    def test_order_item_total_retrieve(self):
        '''
        Test for OrderItem Total retrieval based on the price and  quantity
        '''

        offer = Offer.objects.create(product=self.product, msrp = 80)
        price = offer.sale_price.filter(start_date__lte= timezone.now(), end_date__gte=timezone.now()).order_by('priority').first()
        invoice = Invoice.objects.create(user = self.user, ordered_date = timezone.now())
        orderitem = OrderItem.objects.create(invoice = invoice, offer = offer, price = price)

        try:
            self.assertEqual(orderitem.total(), (price.cost * orderitem.quantity))

        except:     # Only print results if there is an error, but continue to raise the error for the testing tool
            print("")
            print(orderitem.price.all())
            print(orderitem.quantity)
            raise


#######################
# PURCHASES MODEL TEST
#######################

class PurchasesModelTest(TestCase):
    '''
    Test for Purchases Model Test
    '''

    def setUp(self):
        pass
