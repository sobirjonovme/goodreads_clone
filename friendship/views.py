from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .models import FriendRequest
from users.models import CustomUser


# Create your views here.
class SendFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        from_user = request.user
        to_user = CustomUser.objects.get(id=user_id)

        if from_user == to_user:
            messages.info(request, "You cannot send friend request to yourself", extra_tags='danger')
        else:
            friend_request, created = FriendRequest.objects.get_or_create(
                from_user=from_user,
                to_user=to_user
            )
            # friend_request -> FriendRequest object itself
            # created -> boolen (is new object created or not)

            if created:
                messages.info(request, "Friend request sent")
            else:
                messages.info(request, "Friend Request was already sent", extra_tags='danger')

        return redirect(reverse('users:profile', kwargs={"username": to_user.username}))


class CancelFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        from_user = request.user
        to_user = CustomUser.objects.get(id=user_id)
        friend_request = FriendRequest.objects.get(from_user=from_user, to_user=to_user)
        friend_request.delete()

        messages.success(request, "Friend request cancelled")

        return redirect(reverse('users:profile', kwargs={"username": to_user.username}))


class ResponseToFriendRequestView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        friend_request = FriendRequest.objects.get(id=self.kwargs['request_id'])
        return self.request.user == friend_request.to_user

    def get(self, request, request_id):
        friend_request = FriendRequest.objects.get(id=request_id)
        from_user = friend_request.from_user
        answer = request.GET.get('answer')
        # Where requested from and where redirect again
        where = request.GET.get('where', 'profile')

        if answer == 'accept':
            friend_request.to_user.friends.add(from_user)
            from_user.friends.add(friend_request.to_user)
            friend_request.delete()
            messages.success(request, f"You accepted friend request from {from_user}")
        if answer == 'reject':
            friend_request.delete()
            messages.info(request, f"You rejected friend request from {from_user}", extra_tags='danger')

        # Where requested from and where redirect again
        if where == 'request-list':
            return redirect('friendship:request-list')
        return redirect(reverse('users:profile', kwargs={'username': from_user.username}))


class RemoveFriendView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        target_user = CustomUser.objects.get(id=user_id)
        request.user.friends.remove(target_user)
        target_user.friends.remove(request.user)

        messages.info(request, 'Friendship cancelled successfully')

        return redirect(reverse('users:profile', kwargs={'username': target_user.username}))


class FriendRequestListView(LoginRequiredMixin, View):
    def get(self, request):
        request_list = request.user.to_user.all().order_by('-id')

        return render(request, 'friendship/request_list.html', {'request_list': request_list})


class FriendListView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        friend_list = user.friends.all().order_by('username')

        return render(request, 'friendship/friend_list.html', {'friend_list': friend_list})
