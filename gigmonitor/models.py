from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=200)
    spotify_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    soundcloud_id = models.CharField(max_length=200, unique=True, null=True)
    resident_advisor_id = models.CharField(max_length=200, unique=True, null=True)
    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    date = models.DateTimeField()
    artists = models.ManyToManyField(Artist)

    def __str__(self):
        return self.title


