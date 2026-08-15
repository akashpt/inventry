from django.shortcuts import render,redirect

# Create your views here.

def index(request):
    return render(request, "index.html")


def customer(request):
    return render(request, "customer.html")


def newcustomer(request):
    return render(request, "newcustomer.html")

def merchant(request):
    return render(request, "merchant.html")

def newmerchant(request):
    return render(request, "newmerchant.html")

def products(request):
    return render(request, "products.html")

def invoice(request):
    return render(request, "invoice.html")