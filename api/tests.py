import time

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from users.models import CustomUser
from books.models import Book, BookReview


# Create your tests here.
class BookReviewAPITestCase(APITestCase):
    def setUp(self):
        # to create test User
        self.user = CustomUser.objects.create(
            username='TestUserName',
            first_name='TestFirsName',
            last_name='TestLastName',
            email='testemail@gmail.com'
        )
        self.user.set_password('parol12345')
        self.user.save()
        # to login with this user
        self.client.login(username='TestUserName', password='parol12345')

        # to create test Book
        self.book = Book.objects.create(title='Book Title', description='Test book description', isbn='123456789')

    def test_book_review_detail_with_logged_in_user(self):
        # to create Book Review
        review = BookReview.objects.create(
            stars_given=5, comment_text='Very Nice book!',
            book=self.book, user=self.user
        )
        # to get API response
        response = self.client.get(reverse('api:review-detail', kwargs={'review_id': review.id}))

        # to check if api details are correct
        self.assertEqual(response.status_code, 200)
        # review details
        self.assertEqual(response.data['id'], review.id)
        self.assertEqual(response.data['stars_given'], review.stars_given)
        self.assertEqual(response.data['comment_text'], review.comment_text)
        # review owner details
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['first_name'], self.user.first_name)
        self.assertEqual(response.data['user']['last_name'], self.user.last_name)
        self.assertEqual(response.data['user']['email'], self.user.email)
        # book details
        self.assertEqual(response.data['book']['id'], self.book.id)
        self.assertEqual(response.data['book']['title'], self.book.title)
        self.assertEqual(response.data['book']['description'], self.book.description)
        self.assertEqual(response.data['book']['isbn'], self.book.isbn)

    def test_book_review_without_logged_in_user(self):
        # to Log Out
        self.client.logout()
        # to create review
        review = BookReview.objects.create(
            stars_given=5, comment_text='Nice Book!',
            book=self.book, user=self.user
        )

        # to try to get API Response
        response1 = self.client.get(reverse('api:review-detail', kwargs={'review_id': review.id}))
        response2 = self.client.get(reverse('api:review-list'))
        response3 = self.client.get(reverse('api:book-list'))

        # to check if we get 403 Forbidden
        self.assertEqual(response1.status_code, 403)
        self.assertEqual(response2.status_code, 403)
        self.assertEqual(response3.status_code, 403)

    def test_delete_book_review(self):
        review = BookReview.objects.create(
            stars_given=4, comment_text='Good Book!',
            user=self.user, book=self.book
        )

        # to delete this review via API request
        response = self.client.delete(reverse('api:review-detail', kwargs={'review_id': review.id}))

        # to check response status code
        self.assertEqual(response.status_code, 204)
        # to check review deleted successfully
        self.assertFalse(BookReview.objects.filter(id=review.id).exists())

    def test_patch_book_review(self):
        review = BookReview.objects.create(
            stars_given=4, comment_text='Good Book!',
            user=self.user, book=self.book
        )

        # to edit book review via PATCH request method
        response = self.client.patch(
            reverse('api:review-detail', kwargs={'review_id': review.id}),
            data={'stars_given': 2}
        )

        # to check response status
        self.assertEqual(response.status_code, 200)
        # to check Stars_Given was updated successfully
        review.refresh_from_db()
        self.assertEqual(review.stars_given, 2)

    def test_put_book_review(self):
        review = BookReview.objects.create(
            stars_given=4, comment_text='Good Book!',
            user=self.user, book=self.book
        )

        # to edit book review via PUT request method
        response = self.client.put(
            reverse('api:review-detail', kwargs={'review_id': review.id}),
            data={
                "stars_given": 2, "comment_text": "Bad book!",
                "book_id": self.book.id, "user_id": self.user.id
            }
        )

        # to check response status
        self.assertEqual(response.status_code, 200)
        # to check Review Details was updated successfully
        review.refresh_from_db()
        self.assertEqual(review.stars_given, 2)
        self.assertEqual(review.comment_text, 'Bad book!')

    def test_create_book_review(self):
        data = {
            'stars_given': 2, 'comment_text': 'Bad book!',
            'user_id': self.user.id, 'book_id': self.book.id
        }

        # to create book review via POST request method
        response = self.client.post(reverse('api:review-list'), data=data)

        # to check response status
        self.assertEqual(response.status_code, 201)

        # to get BookReview from database
        review = BookReview.objects.get(book=self.book)
        # to check Review was created successfully
        self.assertEqual(review.stars_given, 2)
        self.assertEqual(review.comment_text, 'Bad book!')
        self.assertEqual(review.user.id, self.user.id)

    def test_book_review_list(self):
        # to create First Book Review
        review_1 = BookReview.objects.create(
            stars_given=5, comment_text='Very nice book!',
            book=self.book, user=self.user
        )

        time.sleep(0.1)
        # to create Second Book
        book_2 = Book.objects.create(title='Book title 2', description='Book Description 2', isbn='223214213')
        # to create Secon Book Rerview
        review_2 = BookReview.objects.create(
            stars_given=2, comment_text='Bad book. I don\'t like it',
            book=book_2, user=self.user
        )

        # to get API Response from Review-List
        response = self.client.get(reverse('api:review-list'))

        # to check if API response details are correct
        self.assertEqual(response.status_code, 200)
        # to check all review are included in response
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 2)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

        # to check Review List objects
        # Note that: reviews are Ordered by their created date, So Last In First Out
        self.assertEqual(response.data['results'][0]['id'], review_2.id)
        self.assertEqual(response.data['results'][0]['stars_given'], review_2.stars_given)
        self.assertEqual(response.data['results'][0]['comment_text'], review_2.comment_text)
        self.assertEqual(response.data['results'][1]['id'], review_1.id)
        self.assertEqual(response.data['results'][1]['stars_given'], review_1.stars_given)
        self.assertEqual(response.data['results'][1]['comment_text'], review_1.comment_text)

