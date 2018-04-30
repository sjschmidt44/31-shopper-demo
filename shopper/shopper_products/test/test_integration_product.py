from django.test import TestCase
from shopper_profile.models import User
from ..models import Product, Photo
from model_mommy import mommy
import tempfile
import factory


class TestStoreRoutes(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls)

        for n in range(10):
            user = mommy.make(User)
            user.set_password('password')
            user.save()
            product = mommy.make(Product, user=user)
            mommy.make(
                Photo,
                product=product,
                image=tempfile.NamedTemporaryFile(suffix='.png').name)

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        super(TestCase, cls)

    def test_200_status_on_authenticated_request_to_store(self):
        user = User.objects.first()
        # self.client.login(username=user.username, password='password')
        self.client.force_login(user)
        response = self.client.get('/store/')
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_200_status_on_authenticated_request_to_product(self):
        user = User.objects.first()
        product = Product.objects.first()
        self.client.force_login(user)
        response = self.client.get('/store/products/{}'.format(product.id))
        self.client.logout()
        self.assertEqual(response.status_code, 200)

    def test_302_status_on_unauthenticated_request_to_product(self):
        product = Product.objects.first()
        response = self.client.get('/store/products/{}'.format(product.id))
        self.assertEqual(response.status_code, 302)

    def test_404_status_on_bad_request_to_product(self):
        response = self.client.get('/store/products/does_not_exist')
        self.assertEqual(response.status_code, 404)

    def test_302_status_on_unauthenticated_request_to_store(self):
        response = self.client.get('/store/')
        self.assertEqual(response.status_code, 302)

    def test_only_public_products_are_shown(self):
        user = User.objects.first()
        product = Product.objects.first()
        product.published = 'PUBLIC'
        product.save()

        self.client.force_login(user)
        response = self.client.get('/store/')
        self.client.logout()

        products = response.context['products']
        for prod in products:
            self.assertEqual(prod.published, 'PUBLIC')
