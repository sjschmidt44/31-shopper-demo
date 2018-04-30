from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from .models import ShopperProfile, User
from django.http import Http404
from django.test import Client
from faker import Faker
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker('user_name')
    email = factory.Faker('email')


def define_profile(user):
    fake = Faker()
    user.profile.street = fake.street_address()
    user.profile.city = fake.city()
    user.profile.state = fake.state_abbr()
    user.profile.zip_code = fake.zipcode()
    user.profile.cell = fake.phone_number()
    user.profile.home = fake.phone_number()


class ProfileTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls)
        for _ in range(50):
            user = UserFactory.create()
            user.set_password(factory.Faker('password'))
            user.save()
            define_profile(user)
            user.profile.save()

    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls)
        User.objects.all().delete()

    def test_user_can_point_to_its_profile(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile)

    def test_profile_has_street(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile.street)

    def test_profile_has_city(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile.city)

    def test_profile_has_state(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile.state)

    def test_profile_has_zip_code(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile.zip_code)

    def test_profile_has_cell(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile.cell)

    def test_profile_has_home(self):
        one_user = User.objects.all()[0]
        self.assertIsNotNone(one_user.profile.home)

    def test_profile_is_active(self):
        one_user = User.objects.all()[0]
        self.assertTrue(one_user.is_active)

    def test_profile_is_created_when_user_is_updated(self):
        self.assertEquals(ShopperProfile.objects.count(), 50)
        one_user = User.objects.last()
        one_user.username = 'GandalfTheWhite'
        one_user.save()
        self.assertEquals(ShopperProfile.objects.count(), 50)

    def test_all_items_in_active(self):
        """Test that active method gets all active profiles."""
        one_user = User.objects.last()
        one_user.is_active = False
        one_user.save()

        active_profiles = ShopperProfile.active
        all_profiles = ShopperProfile.objects.all()
        self.assertEquals(active_profiles.count(), all_profiles.count() - 1)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        user = UserFactory(username='gandalf', email='wizard@middle.earth')
        user.set_password('password')
        user.save()

        user.profile.street = '1234 Candy Land'
        user.profile.city = 'Candy Land'
        user.profile.state = 'CL'
        user.profile.zip_code = '12345'
        user.profile.cell = '123-456-7890'
        user.profile.home = '123-456-7890'
        user.profile.save()

        self.gandalf = user

    def tearDown(self):
        User.objects.all().delete()

    def test_profile_view_shows_please_login_when_unauthenticated(self):
        from .views import profile_view
        request = self.request.get('/profile/')
        request.user = AnonymousUser()
        response = profile_view(request, 'gandalf')
        self.assertIn(b'Please log into the site', response.content)

    def test_profile_view_with_no_user_name_not_logged_in_redirets_home(self):
        from .views import profile_view
        request = self.request.get('/profile/')
        request.user = AnonymousUser()
        response = profile_view(request)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_with_bad_user_returns_404(self):
        from .views import profile_view
        request = self.request.get('/profile/')
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            profile_view(request, 'Bilbo')

    def test_profile_view_with_logged_in_user_gets_user_profile(self):
        from .views import profile_view
        request = self.request.get('/profile/')
        request.user = self.gandalf
        response = profile_view(request)
        self.assertIn(b'profile for gandalf', response.content)


class SettingsViewTest(TestCase):
    pass


class ProfileRouteTests(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        user_one = UserFactory(username='gandalf', email='wizard@middle.earth')
        user_one.set_password('password')
        user_one.save()

        user_one.profile.street = '1234 Candy Land'
        user_one.profile.city = 'Candy Land'
        user_one.profile.state = 'CL'
        user_one.profile.zip_code = '12345'
        user_one.profile.cell = '123-456-7890'
        user_one.profile.home = '123-456-7890'
        user_one.profile.save()

        user_two = UserFactory(username='bilbo', email='hobbit@middle.earth')
        user_two.set_password('password')
        user_two.save()

        user_two.profile.street = '4567 Candy Land'
        user_two.profile.city = 'Candy Land'
        user_two.profile.state = 'CL'
        user_two.profile.zip_code = '12345'
        user_two.profile.cell = '321-654-7890'
        user_two.profile.home = '321-654-7890'
        user_two.profile.save()

        self.gandalf = user_one
        self.bilbo = user_two

    def tearDown(self):
        User.objects.all().delete()

    def test_profile_route_has_200_response_given_an_authenticated_user(self):
        c = Client()
        c.login(username=self.gandalf.username, password='password')
        response = c.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_profile_route_has_user_info(self):
        c = Client()
        c.login(username=self.gandalf.username, password='password')
        response = c.get('/profile/')
        self.assertEqual(
            response.context['user'].username, self.gandalf.username)

    def test_profile_route_does_not_allow_editing_for_other_users(self):
        c = Client()
        c.login(username=self.gandalf.username, password='password')
        response = c.get('/profile/bilbo')
        self.assertNotIn(b'Edit Profile', response.content)

    def test_profile_route_does_allow_editing_for_signed_in_users(self):
        c = Client()
        c.login(username=self.gandalf.username, password='password')
        response = c.get('/profile/gandalf')
        self.assertIn(b'Edit Profile', response.content)

    def test_profile_route_returns_404_if_user_does_not_exist(self):
        c = Client()
        response = c.get('/profile/does_not_exist')
        self.assertEqual(response.status_code, 404)

    def test_profile_route_redirects_if_not_logged_in(self):
        c = Client()
        response = c.get('/profile/')
        self.assertEqual(response.status_code, 302)
