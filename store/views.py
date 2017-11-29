from django.shortcuts import render
from .models import Book

# Create your views here.

def index(request):
	return render(request,'template.html')


def store(request):
	Books = Book.objects.all()
	context = {
		'books':Books,
	}
	return render(request,'base.html',context)

def book_details(request, book_id):
	context = {
		'book':Book.objects.get(pk=book_id),
	}
	return render(request,'store/detail.html',context)

