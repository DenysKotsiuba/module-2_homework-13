from django.contrib.postgres.fields import ArrayField
from django.db import models


class Quote(models.Model):
    tags = ArrayField(models.CharField(max_length=50))
    quote = models.TextField()
    author = models.ForeignKey("authors.Author", on_delete=models.CASCADE, default=1)