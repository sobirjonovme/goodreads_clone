from django import forms

from .models import BookReview


class BookReviewForm(forms.ModelForm):
    # stars_given field'ini override qilamiz
    # Frontend qismida faqat 1 dan 5 gacha qiymat olishi uchun
    stars_given = forms.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = BookReview
        fields = ('stars_given', 'comment_text')
