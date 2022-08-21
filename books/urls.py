from django.urls import path

from .views import (
    BookListView,
    BookDetailView,
    AddBookReviewView,
    BookReviewUpdateView,
    BookReviewDeleteConfirmView,
    BookReviewDeleteView
)


app_name = 'books'

urlpatterns = [
    path('', BookListView.as_view(), name='list'),
    path('<int:book_id>/', BookDetailView.as_view(), name='detail'),
    path('<int:book_id>/review/', AddBookReviewView.as_view(), name='add_review'),
    path('<int:book_id>/reviews/<int:review_id>/edit/', BookReviewUpdateView.as_view(), name='review-edit'),
    path(
        '<int:book_id>/reviews/<int:review_id>/delete/confirm/',
        BookReviewDeleteConfirmView.as_view(),
        name='confirm-delete-review'
    ),
    path(
        '<int:book_id>/review/<int:review_id>/delete/',
        BookReviewDeleteView.as_view(),
        name='delete-review'
    )
]
