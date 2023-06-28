from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Author
from .forms import AuthorForm


def author(request, author_fullname):
    author = Author.objects.get(fullname=author_fullname)
    return render(request, "authors/author.html", context={"author": author})

@login_required
def add_author(request):
    form_class = AuthorForm

    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            fullname = form.cleaned_data["fullname"]
            form.save()
            return redirect(to="authors:author", author_fullname=fullname)

        return render(request, "authors/add_author.html", context={"form": form})
    
    return render(request, "authors/add_author.html", context={"form": form_class})
