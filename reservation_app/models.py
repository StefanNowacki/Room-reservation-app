from django.db import models


# Create your models here.


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capacity = models.IntegerField()
    projector = models.BooleanField(default=False)


class Reservation(models.Model):
    date = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    comment = models.TextField(null=True)

    class Meta:
        unique_together = ('date', 'room')
