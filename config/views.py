from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator

from books.models import BookReview


def landing_page(request):
    return render(request, 'landing.html')


def home_page_view(request):
    # reviews filter
    filter_by = request.GET.get('filter', 'all')

    if filter_by == 'all':
        review_list = BookReview.objects.all().order_by('-create_at')
        button_activity = ['info', 'secondary', 'secondary']
    else:
        if request.user.is_authenticated:
            if filter_by == 'by_friends':
                # review only written by request users friends
                review_list = BookReview.objects.filter(user__friends=request.user).order_by('-create_at')
                button_activity = ['secondary', 'info', 'secondary']
            elif filter_by == 'my_reviews':
                # review only written by mine
                review_list = BookReview.objects.filter(user=request.user).order_by('-create_at')
                button_activity = ['secondary', 'secondary', 'info']
        else:
            return redirect(reverse('users:login'))

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
        {'page_reviews': page_reviews, 'page_range': page_range, 'button_activity': button_activity}
    )
