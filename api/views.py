from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from books.models import BookReview, Book
from .serializers import BookReviewSerializer, BookSerializer


# Create your views here.
class BookReviewDetailAPIView(APIView):
    # Bu Page'ga kimlar kira olishini belgilaymiz.
    # Bunda talab qilinadigan narsalarni list shaklida beramiz
    # bizning holatda faqat IsAuhernticated bo'lganligi talab qilinadi xolos
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id):
        book_review = BookReview.objects.get(id=review_id)
        serializer = BookReviewSerializer(book_review)

        return Response(data=serializer.data)

    def delete(self, request, review_id):
        book_review = BookReview.objects.get(id=review_id)
        book_review.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, review_id):
        book_review = BookReview.objects.get(id=review_id)
        serializer = BookReviewSerializer(instance=book_review, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, review_id):
        book_review = BookReview.objects.get(id=review_id)
        serializer = BookReviewSerializer(instance=book_review, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewListAPIView(APIView):
    # Bu Page'ga kimlar kira olishini belgilaymiz.
    # Bunda talab qilinadigan narsalarni list shaklida beramiz
    # bizning holatda faqat IsAuhernticated bo'lganligi talab qilinadi xolos
    permission_classes = [IsAuthenticated]

    def get(self, request):
        book_review_list = BookReview.objects.all().order_by('-create_at')

        # Rest Framework Pagination
        paginator = PageNumberPagination()
        # page_size va page (nechanchi page ekanligi) parametrlarini request'dan o'zi ovoladi
        page_obj = paginator.paginate_queryset(book_review_list, request)

        # serializer orqali json formatga o'tkazamiz
        serializer = BookReviewSerializer(page_obj, many=True)

        # PageNumberPagination class'ining maxsus get_paginated_response funksiyasidan foydalanamiz
        # return Response(data=serializer.data) funksiyasining o'rniga
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BookReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)

        return Response(data=serializer.data)
