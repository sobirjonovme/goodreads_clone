from django.test import TestCase
from django.urls import reverse

import time

from books.models import BookReview, Book
from users.models import CustomUser


class HomePageTestCase(TestCase):
    def test_no_reviews(self):
        response = self.client.get(reverse('home_page'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Reviews found')
        self.assertQuerysetEqual(response.context['page_reviews'], [])

    def test_paginated_reviews_list(self):
        # to create book
        book = Book.objects.create(title='TestTitle', description='TestDescription', isbn='1234214')

        # to create user
        user = CustomUser.objects.create(
            username='TestUserName',
            first_name='TestFirstName',
            last_name='TestLastName'
        )
        user.set_password('parol12345')
        user.save()

        # to create BookReview
        # Bunda vaqtlar deyarli bir xil bo'lgani uchun tartibni to'g'ri qo'ya olmadik
        # Shu bois 0.1 sekund sleep() funksiyasini qo'shdik
        review1 = BookReview.objects.create(book=book, user=user, comment_text='Very nice book!', stars_given=5)
        time.sleep(0.1)
        review2 = BookReview.objects.create(book=book, user=user, comment_text='Useful book!', stars_given=4)
        time.sleep(0.1)
        review3 = BookReview.objects.create(book=book, user=user, comment_text='Good book!', stars_given=3)

        # to get response from home page
        # -----------  page 1 ------------------
        response = self.client.get(reverse('home_page') + '?page_size=2')
        self.assertQuerysetEqual(response.context['page_reviews'], [review3, review2])
        self.assertContains(response, review3.comment_text)
        self.assertContains(response, review2.comment_text)
        # --------------  page 2  ---------------
        response = self.client.get(reverse('home_page') + '?page_size=2&page=2')
        self.assertQuerysetEqual(response.context['page_reviews'], [review1])
        self.assertContains(response, review1.comment_text)

