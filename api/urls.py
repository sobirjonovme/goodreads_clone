from django.urls import path

from .views import BookReviewDetailAPIView, BookListAPIView, ReviewListAPIView


app_name = 'api'

urlpatterns = [
    path('reviews/<int:review_id>/', BookReviewDetailAPIView.as_view(), name='review-detail'),
    path('reviews/', ReviewListAPIView.as_view(), name='review-list'),
    path('books/', BookListAPIView.as_view(), name='book-list')
]
