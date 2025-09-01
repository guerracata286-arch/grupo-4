from django.db import models
from django.utils import timezone
from django.conf import settings

class Room(models.Model):
    code = models.CharField(max_length=1, unique=True)  # 'A', 'B', 'C'
    def __str__(self): return self.code

class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class RoomInventory(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ("room","material")

class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Reserva {self.room.code} {self.date} {self.start_time}-{self.end_time}"

class ReservationItem(models.Model):
    reservation = models.ForeignKey(Reservation, related_name="items", on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

class Blackout(models.Model):
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=["room","start_datetime","end_datetime"])]

    def __str__(self):
        scope = self.room.code if self.room_id else "GLOBAL"
        return f"{scope}: {self.start_datetime}–{self.end_datetime} ({self.reason})"
