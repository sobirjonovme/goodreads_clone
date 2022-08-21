from django.test import TestCase
from django.urls import reverse

from .models import Book, Author, BookAuthor, BookReview
from users.models import CustomUser


# Create your tests here.
class BooksTestCase(TestCase):
    def test_no_books(self):
        response = self.client.get(reverse('books:list'))
        # print(response)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No books found.')
        self.assertQuerysetEqual(response.context['page_obj'].object_list, [])

    def test_book_list(self):
        book1 = Book.objects.create(title='Book 1', description='Description 1', isbn='111111')
        book2 = Book.objects.create(title='Book 2', description='Description 2', isbn='222222')
        book3 = Book.objects.create(title='Book 3', description='Description 3', isbn='333333')

        # Eng oxirgi yaratilgani birinchi chiqadi
        response = self.client.get(reverse('books:list') + "?page_size=2")
        for book in [book3, book2]:
            self.assertContains(response, book.title)
        self.assertNotContains(response, book1.title)

        response = self.client.get(reverse('books:list') + '?page=2&page_size=2')
        self.assertContains(response, book1.title)

    def test_book_detail(self):
        # no author
        book = Book.objects.create(title='Book 1', description='Description 1', isbn='111111')

        response = self.client.get(reverse('books:detail', kwargs={'book_id': book.id}))

        self.assertEqual(response.status_code, 200)
        # print(response.context['book'].description)
        self.assertEqual(response.context['book'], book)
        self.assertContains(response, book.title)
        self.assertContains(response, book.description)
        # checking Unknown author
        self.assertContains(response, 'Unknown')

    def test_book_author_detail(self):
        # to create book
        book = Book.objects.create(title='Book Title', description='Book Description', isbn='12312312')
        # to create author
        author = Author.objects.create(
            first_name='Palonchi',
            last_name='Pistonchiyev',
            email='palonemail@gmail.com',
            bio='1992-yilda tugilgan'
        )
        # to connect Book and Auhtor via many-to-many relationship
        book_author = BookAuthor.objects.create(book=book, author=author)

        # to enter book detail page
        response = self.client.get(reverse('books:detail', kwargs={'book_id': book.id}))

        # checking
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['book'].bookauthor_set.all(), [book_author])
        self.assertContains(response, author)
        self.assertNotContains(response, 'Unknown')

    def test_search_book(self):
        book1 = Book.objects.create(title='Book 1', description='Description 1', isbn='111111')
        book2 = Book.objects.create(title='Book 2', description='Description 2', isbn='222222')
        book3 = Book.objects.create(title='Book 3 1', description='Description 3', isbn='333333')

        # searching for '1' key
        # 1st page, there must be Book3. Because the newest one will be first
        response = self.client.get(reverse('books:list'), data={"q": '1', 'page_size': 1, 'page': 1})
        self.assertContains(response, book3.title)
        self.assertNotContains(response, book2.title)
        self.assertNotContains(response, book1.title)
        # 2nd page, there must be Book1. Because the oldest one will be the lastest
        response = self.client.get(reverse('books:list'), data={"q": '1', 'page_size': 1, 'page': 2})
        self.assertContains(response, book1.title)
        self.assertNotContains(response, book2.title)
        self.assertNotContains(response, book3.title)

        # searching for 2nd book
        response = self.client.get(reverse('books:list'), data={"q": '2'})
        self.assertContains(response, book2.title)
        self.assertNotContains(response, book3.title)
        self.assertNotContains(response, book1.title)

        # searching for 3rd book
        response = self.client.get(reverse('books:list'), data={"q": '3'})
        self.assertContains(response, book3.title)
        self.assertNotContains(response, book2.title)
        self.assertNotContains(response, book1.title)


class BookReviewTestCase(TestCase):
    def test_add_review(self):
        # to create book
        book = Book.objects.create(title='Book Title', description='Book Description', isbn='124132413')

        # we need logged in user
        user = CustomUser.objects.create(
            username="TestUserName",
            first_name="TestFirstName",
            last_name="TestLastName"
        )
        user.set_password("parol12345")
        user.save()
        # to login
        self.client.login(username="TestUserName", password="parol12345")

        # to add comment to book
        response = self.client.post(
            reverse("books:add_review", kwargs={"book_id": book.id}),
            data={"stars_given": 4, "comment_text": 'Nice book!'}
        )

        book_reviews = book.bookreview_set.all()

        self.assertEqual(book_reviews.count(), 1)
        self.assertEqual(book_reviews[0].stars_given, 4)
        self.assertEqual(book_reviews[0].comment_text, 'Nice book!')
        self.assertEqual(book_reviews[0].book, book)
        self.assertEqual(book_reviews[0].user, user)
        # to check correct redirect
        self.assertEqual(response.url, reverse("books:detail", kwargs={'book_id': book.id}))

    def test_edit_review_with_correct_user(self):
        # to create book
        book = Book.objects.create(title='Book Title', description='Book Description', isbn='124132413')
        # to create user
        user = CustomUser.objects.create(username="TestUserName")
        user.set_password('parol12345')
        user.save()
        # to craete review
        review = BookReview.objects.create(
            user=user, book=book,
            stars_given=4, comment_text='Nice book!'
        )
        # to login user
        self.client.login(username='TestUserName', password='parol12345')

        # to check get method of edit page
        # to get response
        response = self.client.get(reverse('books:review-edit', kwargs={'book_id': book.id, 'review_id': review.id}))
        # to check form contains review details
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, review.comment_text)
        self.assertContains(response, review.stars_given)

        # to check post method of edit page
        # to change review details
        response = self.client.post(
            reverse('books:review-edit', kwargs={'book_id': book.id, 'review_id': review.id}),
            data={"stars_given": 2, "comment_text": 'Bad book'}
        )
        # to check correct redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('books:detail', kwargs={'book_id': book.id}))
        # to check review details updated
        review.refresh_from_db()
        self.assertEqual(review.stars_given, 2)
        self.assertEqual(review.comment_text, 'Bad book')

    def test_edit_review_with_another_user(self):
        # to create book
        book = Book.objects.create(title='Book Title', description='Book Description', isbn='124132413')
        # to create users
        # to create review owener user
        review_owner = CustomUser.objects.create(username="ReviewOwner")
        review_owner.set_password('parol12345')
        review_owner.save()
        # to create another user for test
        another_user = CustomUser.objects.create(username="AnotherUser")
        another_user.set_password('parol12345')
        another_user.save()
        # to craete review
        review = BookReview.objects.create(
            user=review_owner, book=book,
            stars_given=4, comment_text='Nice book!'
        )
        # to login with another user and try to change review details
        self.client.login(username='AnotherUser', password='parol12345')

        # to check get method of edit page
        # to try to enter edit page by another user (not real owner of review)
        response = self.client.get(reverse('books:review-edit', kwargs={'book_id': book.id, 'review_id': review.id}))
        # to check form contains review details
        self.assertEqual(response.status_code, 403)

        # to check post method of edit page
        # to try to change review details by another user (not real owner of review)
        response = self.client.post(
            reverse('books:review-edit', kwargs={'book_id': book.id, 'review_id': review.id}),
            data={"stars_given": 2, "comment_text": 'Bad book'}
        )
        # to check review not updated and keep old details
        review.refresh_from_db()
        self.assertEqual(review.stars_given, 4)
        self.assertEqual(review.comment_text, 'Nice book!')

    def test_delete_review_wit_correct_user(self):
        # to create book
        book = Book.objects.create(title='Book Title', description='Book Description', isbn='124132413')
        # to create user
        user = CustomUser.objects.create(username="TestUserName")
        user.set_password('parol12345')
        user.save()
        # to craete review
        review = BookReview.objects.create(
            user=user, book=book,
            stars_given=4, comment_text='Nice book!'
        )
        # to login user
        self.client.login(username='TestUserName', password='parol12345')

        # to check review added database
        review_list = BookReview.objects.all()
        self.assertEqual(review_list.count(), 1)

        # to check Confirm Delete Review page
        response = self.client.get(reverse('books:confirm-delete-review', kwargs={'book_id': book.id, 'review_id': review.id}))
        # to check form contains review details
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, review.comment_text)
        self.assertContains(response, review.stars_given)

        # to check Delete Review page
        response = self.client.get(
            reverse('books:delete-review', kwargs={'book_id': book.id, 'review_id': review.id}))
        # to check correct redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('books:detail', kwargs={'book_id': book.id}))

        # to check if review was deleted
        review_list = BookReview.objects.all()
        self.assertEqual(review_list.count(), 0)

    def test_delete_review_wit_another_user(self):
        # to create book
        book = Book.objects.create(title='Book Title', description='Book Description', isbn='124132413')
        # to create users
        # to create review owener user
        review_owner = CustomUser.objects.create(username="ReviewOwner")
        review_owner.set_password('parol12345')
        review_owner.save()
        # to create another user for test
        another_user = CustomUser.objects.create(username="AnotherUser")
        another_user.set_password('parol12345')
        another_user.save()
        # to craete review
        review = BookReview.objects.create(
            user=review_owner, book=book,
            stars_given=4, comment_text='Nice book!'
        )
        # to login user
        self.client.login(username='AnotherUser', password='parol12345')

        # to check review added database
        review_list = BookReview.objects.all()
        self.assertEqual(review_list.count(), 1)

        # to check Confirm Delete Review page
        response = self.client.get(reverse('books:confirm-delete-review', kwargs={'book_id': book.id, 'review_id': review.id}))
        # to check usercanot enter this page
        self.assertEqual(response.status_code, 403)

        # to check Delete Review page
        response = self.client.get(
            reverse('books:delete-review', kwargs={'book_id': book.id, 'review_id': review.id}))
        # to check user cannot delete review
        self.assertEqual(response.status_code, 403)

        # to check if review was NOT deleted
        review_list = BookReview.objects.all()
        self.assertEqual(review_list.count(), 1)
