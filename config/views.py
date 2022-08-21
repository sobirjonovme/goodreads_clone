from django.shortcuts import render
from django.core.paginator import Paginator

from books.models import BookReview


def landing_page(request):
    return render(request, 'landing.html')


def home_page_view(request):
    review_list = BookReview.objects.all().order_by('-create_at')

    # to get page number from http request
    page = request.GET.get('page', 1)
    # to get page size from http request
    page_size = request.GET.get('page_size', 10)

    paginator = Paginator(review_list, page_size)

    page_reviews = paginator.get_page(page)
    # to get previous and next page numbers range
    page_range = paginator.get_elided_page_range(number=page_reviews.number, on_each_side=2, on_ends=2)

    return render(
        request,
        'home.html',
        {'page_reviews': page_reviews, 'page_range': page_range}
    )
