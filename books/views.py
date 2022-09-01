from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator

from .models import Book, BookReview
from .forms import BookReviewForm


# Create your views here.
class BookListView(View):
    def get(self, request):

        # to get search word
        search_query = request.GET.get('q')
        # check searching or not
        if search_query:
            # get searched books
            books = Book.objects.filter(title__icontains=search_query).order_by('-id')
        else:
            # get all books
            books = Book.objects.all().order_by('-id')

        # to get page number from http request
        page = request.GET.get('page', 1)
        # to get page size from http request
        page_size = request.GET.get('page_size', 5)

        # to dive book objects into pages
        paginator = Paginator(books, page_size)

        # to get specific page we want
        page_obj = paginator.get_page(page)
        # to get previous and next page numbers range
        page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=2)

        return render(
            request,
            'books/book_list.html',
            {'page_obj': page_obj, 'page_range': page_range, 'search_query': search_query}
        )


class BookDetailView(View):
    def get(self, request, book_id):
        book = Book.objects.get(id=book_id)
        reviews = book.bookreview_set.all().order_by('-create_at')

        review_form = BookReviewForm()

        return render(
            request,
            'books/book_detail.html',
            {'book': book, 'reviews_list': reviews, 'review_form': review_form}
        )

    # Alohida class ochamiz LoginRequiredMixin'ni ishlatish uchun
    # def post(self, request, book_id):
    #     book = Book.objects.get(id=book_id)
    #     review_form = BookReviewForm(data=request.POST)
    #     if review_form.is_valid():
    #         BookReview.objects.create(
    #             user=request.user,
    #             book=book,
    #             stars_given=review_form.cleaned_data['stars_given'],
    #             comment_text=review_form.cleaned_data['comment_text']
    #         )
    #         return redirect(reverse('books:detail', kwargs={'book_id': book.id}))
    #     return render(request, 'books/book_detail.html', {'book': book, 'review_form': review_form})


class AddBookReviewView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        book = Book.objects.get(id=book_id)
        review_form = BookReviewForm(data=request.POST)
        if review_form.is_valid():
            BookReview.objects.create(
                user=request.user,
                book=book,
                stars_given=review_form.cleaned_data['stars_given'],
                comment_text=review_form.cleaned_data['comment_text']
            )
            return redirect(reverse('books:detail', kwargs={'book_id': book.id}))

        reviews = book.bookreview_set.all().order_by('-create_at')
        return render(
            request,
            'books/book_detail.html',
            {'book': book, 'reviews_list': reviews, 'review_form': review_form}
        )


class BookReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        """
        UserPassesTestMixin class method to check our code (whatever we write)
        if it returns false, deny enter this page
        if return true, allow to enter this page
        """
        # print(self.kwargs)
        book = Book.objects.get(id=self.kwargs['book_id'])
        review = book.bookreview_set.get(id=self.kwargs['review_id'])
        return review.user == self.request.user

    def get(self, request, book_id, review_id):
        book = Book.objects.get(id=book_id)
        review = book.bookreview_set.get(id=review_id)
        review_form = BookReviewForm(instance=review)

        return render(
            request,
            'books/review_edit.html',
            {'book': book, 'review': review, 'review_form': review_form}
        )

    def post(self, request, book_id, review_id):
        book = Book.objects.get(id=book_id)
        review = book.bookreview_set.get(id=review_id)
        review_form = BookReviewForm(instance=review, data=request.POST)

        if review_form.is_valid():
            review_form.save()

            return redirect(reverse('books:detail', kwargs={'book_id': book.id}))

        return render(
            request,
            'books/review_edit.html',
            {'book': book, 'review': review, 'review_form': review_form}
        )


class BookReviewDeleteConfirmView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        """
        UserPassesTestMixin class method to check our code (whatever we write)
        if it returns false, deny enter this page
        if return true, allow to enter this page
        """
        # print(self.kwargs)
        book = Book.objects.get(id=self.kwargs['book_id'])
        review = book.bookreview_set.get(id=self.kwargs['review_id'])
        return review.user == self.request.user

    def get(self, request, book_id, review_id):
        book = Book.objects.get(id=book_id)
        review = book.bookreview_set.get(id=review_id)

        return render(request, 'books/confirm_delete_review.html', {'book': book, 'review': review})


class BookReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        """
        UserPassesTestMixin class method to check our code (whatever we write)
        if it returns false, deny enter this page
        if return true, allow to enter this page
        """
        # print(self.kwargs)
        book = Book.objects.get(id=self.kwargs['book_id'])
        review = book.bookreview_set.get(id=self.kwargs['review_id'])
        return review.user == self.request.user

    def get(self, request, book_id, review_id):
        book = Book.objects.get(id=book_id)
        review = book.bookreview_set.get(id=review_id)

        # to delete review
        # Modellerdagi tayyor delete funksiyasidan foydalanamiz
        review.delete()

        return redirect(reverse('books:detail', kwargs={'book_id': book.id}))
