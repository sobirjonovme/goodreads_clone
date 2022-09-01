from django.urls import path

from .views import (
    SendFriendRequestView,
    CancelFriendRequestView,
    ResponseToFriendRequestView,
    RemoveFriendView,
    FriendRequestListView,
    FriendListView
)


app_name = "friendship"

urlpatterns = [
    path('<int:user_id>/send_friend_request/', SendFriendRequestView.as_view(), name='send-request'),
    path('<int:user_id>/cancel_friend_request/', CancelFriendRequestView.as_view(), name='cancel-request'),
    path('<int:request_id>/response_to_friend_request/', ResponseToFriendRequestView.as_view(), name='response-request'),
    path('<int:user_id>/remove_friend/', RemoveFriendView.as_view(), name='remove-friend'),
    path('friend_request_list/', FriendRequestListView.as_view(), name='request-list'),
    path('<int:user_id>/friend_list/', FriendListView.as_view(), name='friend-list'),
]
