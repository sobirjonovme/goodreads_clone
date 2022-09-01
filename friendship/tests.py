from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from .models import FriendRequest


# Create your tests here.
class FriendRequestTestCase(TestCase):
    def setUp(self):
        self.user_1 = CustomUser.objects.create(username='TestUser1', first_name='Sarvar')
        self.user_1.set_password('parol12345')
        self.user_1.save()
        self.user_2 = CustomUser.objects.create(username='TestUser2', first_name='Sardor')
        self.user_2.set_password('parol12345')
        self.user_2.save()
        # to Log In with first user (user_1)
        self.client.login(username='TestUser1', password='parol12345')

    def test_send_friend_request_normal_case(self):
        # to send Friend Request to user_2
        response = self.client.get(reverse('friendship:send-request', kwargs={'user_id': self.user_2.id}))

        # to check if FriendRequest was created successfully
        request_count = FriendRequest.objects.count()
        requests = FriendRequest.objects.all()
        self.assertEqual(request_count, 1)
        self.assertEqual(requests[0].from_user, self.user_1)
        self.assertEqual(requests[0].to_user, self.user_2)
        # to check user was redirected profile page correctly
        self.assertEqual(response.url, reverse('users:profile', kwargs={'username': self.user_2.username}))

    def test_send_friend_request_to_himself(self):
        # to send friend request to himself user_1 from himself user_1
        response = self.client.get(reverse('friendship:send-request', kwargs={'user_id': self.user_1.id}))

        # to check if FriendRequest was NOT created, e.g. failed
        request_count = FriendRequest.objects.count()
        self.assertEqual(request_count, 0)
        # to check user was redirected profile page correctly
        self.assertEqual(response.url, reverse('users:profile', kwargs={'username': self.user_1.username}))

    def test_send_friend_request_twice(self):
        # to send friend request to user_2 from user_1 in FIRST time
        self.client.get(reverse('friendship:send-request', kwargs={'user_id': self.user_2.id}))
        # to check if FriendRequest was created successfully
        request_count = FriendRequest.objects.count()
        self.assertEqual(request_count, 1)

        # to send friend request to user_2 from user_1 in SECOND time
        response = self.client.get(reverse('friendship:send-request', kwargs={'user_id': self.user_2.id}))
        # to check FriendRequest was NOT created and failed in SECOND time
        request_count = FriendRequest.objects.count()
        self.assertEqual(request_count, 1)
        # to check user was redirected profile page correctly
        self.assertEqual(response.url, reverse('users:profile', kwargs={'username': self.user_2.username}))

    def test_friend_request_list(self):
        # to create 3rd user (user_3)
        user_3 = CustomUser.objects.create(username='TestUser3', first_name='Rustam')
        user_3.set_password('parol12345')
        user_3.save()
        # to send FriendRequest to user_1 from both user_2 and user_3
        fr1 = FriendRequest.objects.create(from_user=self.user_2, to_user=self.user_1)    # from user_2
        fr2 = FriendRequest.objects.create(from_user=user_3, to_user=self.user_1)     # from user_1

        # to get Friend Request list page response
        response = self.client.get(reverse('friendship:request-list'))

        # to check both FriendRequest exist
        self.assertQuerysetEqual(response.context['request_list'], [fr2, fr1])
        self.assertContains(response, self.user_2.username)
        self.assertContains(response, user_3.username)

    def test_cancel_friend_request(self):
        # to create FriendRequest from user_1 to user_2
        fr = FriendRequest.objects.create(from_user=self.user_1, to_user=self.user_2)
        # to check FriendRequest created succesfully
        requests = FriendRequest.objects.all()
        self.assertQuerysetEqual(requests, [fr])

        # to cancel FriendRequest
        response = self.client.get(reverse('friendship:cancel-request', kwargs={'user_id': self.user_2.id}))

        # to check FriendRequest deleted successfully
        requests = FriendRequest.objects.all()
        self.assertQuerysetEqual(requests, [])
        # to check user redirected target user profile correctly
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('users:profile', kwargs={'username': self.user_2.username}))


class ResponseToFriendRequestTestCase(TestCase):
    def setUp(self):
        self.user_1 = CustomUser.objects.create(username='TestUser1', first_name='Sarvar')
        self.user_1.set_password('parol12345')
        self.user_1.save()
        self.user_2 = CustomUser.objects.create(username='TestUser2', first_name='Sardor')
        self.user_2.set_password('parol12345')
        self.user_2.save()
        # to Log In with first user (user_1)
        self.client.login(username='TestUser1', password='parol12345')
        # to create FriendRequest from user_2 to user_1
        self.fr = FriendRequest.objects.create(from_user=self.user_2, to_user=self.user_1)

    def test_response_to_friend_request_as_another_user(self):
        # to give response to friend request as user who this request is NOT for
        self.client.login(username='TestUser2', password='parol12345')
        response = self.client.get(
            reverse('friendship:response-request', kwargs={"request_id": self.fr.id}) + '?answer=accept'
        )

        # to check if this request failed
        self.assertEqual(response.status_code, 403)
        # to check FriendRequest still exist
        requests = FriendRequest.objects.all()
        self.assertQuerysetEqual(requests, [self.fr])

    def test_positive_response_to_friend_request(self):
        # to give response to FriendRequest with "accept" answer
        response = self.client.get(
            reverse('friendship:response-request', kwargs={'request_id': self.fr.id}) + '?answer=accept'
        )

        # to check FriendRequest deleted successfully
        request_count = FriendRequest.objects.count()
        self.assertEqual(request_count, 0)

        # to check these users are friends now
        self.assertQuerysetEqual(self.user_1.friends.all(), [self.user_2])
        self.assertQuerysetEqual(self.user_2.friends.all(), [self.user_1])

    def test_negative_response_to_friend_request(self):
        # to give response to FriendRequest with "reject" answer
        response = self.client.get(
            reverse('friendship:response-request', kwargs={'request_id': self.fr.id}) + '?answer=reject'
        )

        # to check FriendRequest deleted successfully
        request_count = FriendRequest.objects.count()
        self.assertEqual(request_count, 0)

        # to check these users are NOT friends now
        self.assertQuerysetEqual(self.user_1.friends.all(), [])
        self.assertQuerysetEqual(self.user_2.friends.all(), [])


class FriendsFunctionsTestCase(TestCase):
    def setUp(self):
        self.user_1 = CustomUser.objects.create(username='TestUser1', first_name='Sarvar')
        self.user_1.set_password('parol12345')
        self.user_1.save()
        self.user_2 = CustomUser.objects.create(username='TestUser2', first_name='Sardor')
        self.user_2.set_password('parol12345')
        self.user_2.save()
        # to Log In with first user (user_1)
        self.client.login(username='TestUser1', password='parol12345')
        # to create Friendship between user_1 and user_2
        self.user_1.friends.add(self.user_2)
        self.user_2.friends.add(self.user_1)

    def test_friends_list_page(self):
        # to create 3rd user
        user_3 = CustomUser.objects.create(username='TestUser3', first_name='Jasur')
        user_3.set_password('parol12345')
        user_3.save()
        # to create Friendship between user_1 and user_3
        self.user_1.friends.add(user_3)
        user_3.friends.add(self.user_1)

        # to check friends list page
        response = self.client.get(reverse('friendship:friend-list', kwargs={'user_id': self.user_1.id}))
        self.assertQuerysetEqual(response.context['friend_list'], [self.user_2, user_3])
        self.assertContains(response, self.user_2.username)
        self.assertContains(response, user_3.username)

    def test_revome_friend(self):
        # to check user_1 and user_2 are friends now
        self.assertIn(self.user_2, self.user_1.friends.all())
        self.assertIn(self.user_1, self.user_2.friends.all())
        #       self.assertContains(self.user_2, self.user_1.friends.all())     # not work

        # to remove user_2 from friends list as user_1
        self.client.get(reverse('friendship:remove-friend', kwargs={'user_id': self.user_2.id}))

        # to check user_1 and user_2 are NOT friends now
        self.assertNotIn(self.user_2, self.user_1.friends.all())
        self.assertNotIn(self.user_1, self.user_2.friends.all())
