from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Quote
from .forms import QuoteForm


def main(request, page=1):
    quotes = Quote.objects.all()
    paginator = Paginator(quotes, 10)
    quotes_on_page = paginator.page(page)
    return render(request, "quotes/index.html", context={"quotes": quotes_on_page})


@login_required
def add_quote(request):
    form_class = QuoteForm

    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            quotes = Quote.objects.all()

            return redirect("quotes:root")
        
        return render(request, "quotes/add_quote.html", {"form": form})

    return render(request, "quotes/add_quote.html", {"form": form_class})