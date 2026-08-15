from django.urls import path 
from billing import views

urlpatterns = [ 
    path("", views.index, name="index"),
    path("customer", views.customer, name="customer"),
    path("newcustomer", views.newcustomer, name="newcustomer"),
    path("merchant", views.merchant, name="merchant"),
    path("newmerchant", views.newmerchant, name="newmerchant"),
    path("products", views.products, name="products"),
    path("invoice", views.invoice, name="invoice"),
]