from django.test import TestCase
from django.urls import reverse
from .models import CustomUser
from django.contrib.auth import get_user


# Create your tests here.
class RegistrationTestCase(TestCase):
    def test_user_account_is_created(self):
        self.client.post(
            reverse('users:register'),
            data={
                'username': 'testusername',
                'first_name': 'TestFirstName',
                'last_name': 'TestLastName',
                'email': 'testemail00@gmail.com',
                'password': 'parol12345'
            }
        )

        user = CustomUser.objects.get(username='testusername')

        self.assertEqual(user.first_name, 'TestFirstName')
        self.assertEqual(user.last_name, 'TestLastName')
        self.assertEqual(user.email, 'testemail00@gmail.com')
        self.assertNotEqual(user.password, 'parol12345')
        self.assertTrue(user.check_password('parol12345'))

    def test_required_fields(self):
        response = self.client.post(
            reverse('users:register'),
            data={
                'first_name': 'TestFirstName',
                'email': 'testemail00@gmail.com',
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 0)
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertFormError(response, 'form', 'password', 'This field is required.')

    def test_invalid_email(self):
        response = self.client.post(
            reverse('users:register'),
            data={
                'username': 'testusername',
                'first_name': 'TestFirstName',
                'last_name': 'TestLastName',
                'email': 'testemail00',
                'password': 'parol12345'
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 0)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')

    def test_unique_username(self):
        # create first user
        self.client.post(
            reverse('users:register'),
            data={
                'username': 'testusername',
                'first_name': 'TestFirstName',
                'last_name': 'TestLastName',
                'email': 'testemail111@gmail.com',
                'password': 'parol12345'
            }
        )
        # try to create second user with that the same username
        response = self.client.post(
            reverse('users:register'),
            data={
                'username': 'testusername',
                'first_name': 'TestFirstName_2',
                'last_name': 'TestLastName_2',
                'email': 'testemail222@gmail.com',
                'password': 'parol98765'
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 1)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')


class LoginTestCase(TestCase):
    def setUp(self):
        # DRY - don't repeat yourself
        # har bir test funksiyasi ishga tushishidan oldin bu funksiya yaratiladi
        # va har safar qayta yangi user yaratishga hojat yo'q
        self.db_user = CustomUser.objects.create_user(username='TestUser', first_name='TestName')
        self.db_user.set_password('parol12345')
        self.db_user.save()

    def test_successful_login(self):
        self.client.post(
            reverse('users:login'),
            data={
                'username': 'TestUser',
                'password': 'parol12345'
            }
        )

        # request yuborgan userni ovolamiz
        user = get_user(self.client)

        self.assertTrue(user.is_authenticated)

    def test_wrong_credentials(self):
        # with wrong username
        self.client.post(
            reverse('users:login'),
            data={
                'username': 'Wrong-Username',
                'password': 'parol12345'
            }
        )
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # with wrong password
        self.client.post(
            reverse('users:login'),
            data={
                'username': 'TestUser',
                'password': 'wrong-parol'
            }
        )
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_required_fields(self):
        response = self.client.post(
            reverse('users:login'),
            data={}
        )
        user = get_user(self.client)

        self.assertFalse(user.is_authenticated)
        self.assertFormError(response, 'login_form', 'username', 'This field is required.')
        self.assertFormError(response, 'login_form', 'password', 'This field is required.')

    def test_logout(self):
        # Login with this user details
        self.client.login(username='TestUser', password='parol12345')
        user = get_user(self.client)
        # check if this user is logged in
        self.assertTrue(user.is_authenticated)

        # logout user
        self.client.get(reverse('users:logout'))
        user = get_user(self.client)
        # check if user is logout
        self.assertFalse(user.is_authenticated)


class ProfileTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse('users:profile', kwargs={'username': 'any_username'}))

        # Djangoda redirect funksiyasi 302 status code qaytarishi kerak
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('users:login') + '?next=' + reverse('users:profile', kwargs={'username': 'any_username'}))

    def test_profile_details(self):
        user = CustomUser.objects.create(
            username='testusername',
            first_name='TestFirstName',
            last_name='TestLastName',
            email='testemail@gmail.com'
        )
        user.set_password('parol12345')
        user.save()

        # client'ning login funksiyasi
        self.client.login(username='testusername', password='parol12345')
        response = self.client.get(reverse('users:profile', kwargs={'username': user.username}))

        # status code'ni tekshiramiz
        self.assertEqual(response.status_code, 200)
        # Sahifaga backend'dan kelgan context'da bizning user borligini tekshiramiz
        self.assertEqual(response.context['user'], user)
        # Sahifada bizning user ma'lumotlari chiqayotganini tekshiramiz
        self.assertContains(response, user.username)
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.email)

    def test_update_profile(self):
        user = CustomUser.objects.create(
            username='TestUser',
            first_name='TestFirstName',
            last_name='TestLastName',
            email='testemail@gmail.com'
        )
        user.set_password('parol12345')
        user.save()
        self.client.login(username='TestUser', password='parol12345')

        response = self.client.post(
            reverse('users:profile-edit'),
            data={
                'username': 'TestUser',
                'first_name': 'NewFirstName',
                'last_name': 'NewLastName',
                'email': 'newemail@gmail.com'
            }
        )

        # Hozir user o'zgaruvchisida eski user ma'lumotlari turibdi
        # Biz ya gilagan ma'lumotlarni database'dan boshqatdan user'ga ovolamiz
        # user = CustomUser.objects.get(id=user.id)
        # Bundan yaxshiroq usuli esa har bir modelda bo'ladigan refresh funksiyasi
        user.refresh_from_db()

        self.assertEqual(user.first_name, 'NewFirstName'),
        self.assertEqual(user.last_name, 'NewLastName')
        self.assertEqual(user.email, 'newemail@gmail.com')
        self.assertEqual(response.url, reverse('users:profile', kwargs={'username': user.username}))
