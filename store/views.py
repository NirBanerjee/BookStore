#This is how the views.py looks like

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Book, BookOrder, Cart
from django.core.urlresolvers import reverse
from django.utils import timezone
import paypalrestsdk
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string 
from django.contrib.gis.geoip import GeoIP
import string, random


from .models import Book, BookOrder, Cart, Review
from .forms import ReviewForm


def index(request):
    return render(request, 'template.html')

def store(request):
    books= Book.objects.all()
    context= {
        'books':books,
    }
    return render(request,'base.html',context)

def book_details(request,book_id):
    book= Book.objects.get(pk=book_id)
    context= {
        'book': book,
    }
    if request.user.is_authenticated():
        if request.method== "POST":
            form= ReviewForm(request.POST)
            if form.is_valid():
                new_review= Review.objects.create (
                    user= request.user,
                    book= context['book'],
                    text=form.cleaned_data.get('text'),
                )
                new_review.save()
                if Review.objects.filter(user=request.user).count()<6:
                    subject= 'Your MysteryBooks.com discount code is here'
                    from_email= 'librarian@mysterybooks.com'
                    to_email= [request.user.email]
                    email_context = Context ({
                        'username': request.user.username,
                        'code': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
                        'discount': 10
                    })
                        
                    text_email= render_to_string('email/review_email.txt', email_context)
                    html_email= render_to_string('email/review_email.html', email_context)
                    msg= EmailMultiAlternatives(subject, text_email, from_email, to_email)
                    msg.attach_alternative(html_email, 'text/html')
                    msg.content_subtype= 'html'
                    msg.send()
        else:
            if Review.objects.filter(user=request.user, book=context['book']).count() == 0:
                form= ReviewForm()
                context['form']= form
    context['reviews']= book.review_set.all()
    geo_info=GeoIP().city(request.META.get('REMOTE_ADDR'))
    if not geo_info:
        geo_info= GeoIP().city("103.39.251.45")
    context['geo_info']= geo_info
    return render(request,'store/detail.html',context)

def add_to_cart(request,book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                cart= Cart.objects.get(user=request.user, active =True)
            except ObjectDoesNotExist:
                cart= Cart.objects.create(user=request.user)
                cart.save()
            cart.add_to_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')

def remove_from_cart(request,book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            cart= Cart.objects.get(user=request.user, active =True)
            cart.remove_from_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')    
        
def cart(request):
    if request.user.is_authenticated():
        cart=Cart.objects.filter(user=request.user, active=True)
        orders= BookOrder.objects.filter(cart=cart)
        total = 0
        count= 0
        for order in orders:
            total += (order.book.price * order.quantity)
            count += order.quantity
        context = {
            'cart' : orders,
            'total': total,
            'count': count,
        }
        return render(request, 'store/cart.html', context)
    else:
        return redirect('index')    