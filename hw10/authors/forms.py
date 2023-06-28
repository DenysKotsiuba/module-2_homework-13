from django.forms import ModelForm, CharField, DateField, DateInput, Textarea

from .models import Author


class AuthorForm(ModelForm):
    fullname = CharField(max_length=100)
    born_date = DateField(widget=DateInput(attrs={"placeholder": "YYYY-MM-DD"}))
    born_location = CharField(max_length=250)
    description = CharField(widget=Textarea())

    class Meta:
        model = Author
        fields = ["fullname", "born_date", "born_location", "description"]
