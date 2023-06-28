from django.db import models


class Author(models.Model):
    fullname = models.CharField(max_length=100, unique=True)
    born_date = models.DateField()
    born_location = models.CharField(max_length=250)
    description = models.TextField()

    def __str__(self) -> str:
        return self.fullname