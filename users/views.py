from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .forms import UserCreateForm, UserUpdateForm
from .models import CustomUser
from friendship.models import FriendRequest


# Create your views here.
class RegisterView(View):
    def get(self, request):
        create_form = UserCreateForm()
        return render(request, 'users/register.html', {'form': create_form})

    def post(self, request):
        """create user account"""
        # yozuvli ma'lumotlar data orqali, fayllar esa files orqali olinadi
        create_form = UserCreateForm(
            data=request.POST,
            files=request.FILES
        )

        if create_form.is_valid():
            create_form.save()
            return redirect('users:login')
        else:
            return render(request, 'users/register.html', {'form': create_form})


class LoginView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        return render(request, 'users/login.html', {'login_form': login_form})

    def post(self, request):
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():
            user = login_form.get_user()
            # print(f"\n{user.first_name}\n")
            # django'ding tayyor login funksiyasidan foydalanamiz
            login(request, user)

            # requestga message biriktirib qo'yamiz
            # va u faqat bir marta chiqadi xolos, keyingi safar o'chib ketadi
            messages.success(request, 'You have successfully logged in.')

            return redirect('books:list')
        else:
            return render(request, 'users/login.html', {'login_form': login_form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = CustomUser.objects.get(username=username)
        is_friend = user.friends.filter(username=request.user.username)
        is_friend_request_from_you = FriendRequest.objects.filter(from_user=request.user, to_user=user)
        is_friend_request_to_you = FriendRequest.objects.filter(from_user=user, to_user=request.user)

        return render(
            request,
            'users/profile.html',
            {
                'user': user,
                'is_friend': is_friend,
                'is_friend_request_from_you': is_friend_request_from_you,
                'is_friend_request_to_you': is_friend_request_to_you
            }
        )


class LogOutView(LoginRequiredMixin, View):
    def get(self, request):
        # django'ning tayyor logout funksiyasini chaqirib qo'yishimiz yetarli
        logout(request)
        # requestga message biriktirib qo'yamiz
        # va u faqat bir marta chiqadi xolos, keyingi safar o'chib ketadi
        messages.info(request, 'You have successfully logged out.')
        return redirect('landing_page')


class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        # user ma'lumotlarini o'zgartiradigan formada
        # user'ning hozirgi ma'lumotlarini tayyor yozib qo'yadi
        # instance=request.user orqali
        user_update_form = UserUpdateForm(instance=request.user)
        return render(request, 'users/profile_edit.html', {'update_form': user_update_form})

    def post(self, request):
        # instance=request.user bo'lsa mavjud user ma'lumotlarini yangilaydi
        # aks holda CreateView'dek yangi account yaratishga urinadi
        user_update_form = UserUpdateForm(
            instance=request.user,
            data=request.POST,
            files=request.FILES
        )

        if user_update_form.is_valid():
            user_update_form.save()
            messages.success(request, "You have successfully updated your profile.")
            return redirect(reverse('users:profile', kwargs={'username': request.user.username}))
        else:
            return render(request, 'users/profile_edit.html', {'update_form': user_update_form})
