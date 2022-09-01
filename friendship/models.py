from django.db import models

from users.models import CustomUser


# Create your models here.
class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        CustomUser,
        related_name='from_user',
        on_delete=models.CASCADE
    )

    to_user = models.ForeignKey(
        CustomUser,
        related_name='to_user',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.from_user} to {self.to_user}"
