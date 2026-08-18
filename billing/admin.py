from django.contrib import admin

from .models import Customer, FinanceEntry, Invoice, Merchant, PettyCashTransaction, Product


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "company_name", "email", "mobile", "status", "created_at")
    search_fields = ("display_name", "company_name", "email", "mobile")


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("display_name", "company_name", "email", "mobile", "status", "created_at")
    search_fields = ("display_name", "company_name", "email", "mobile")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "sale_price", "stock_quantity", "status")
    search_fields = ("name", "sku", "category")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "invoice_date", "due_date", "amount", "status")
    search_fields = ("invoice_number", "customer__display_name")


@admin.register(FinanceEntry)
class FinanceEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_type", "title", "entry_date", "party_name", "amount", "status")
    list_filter = ("entry_type", "status")
    search_fields = ("title", "party_name", "reference_no")


@admin.register(PettyCashTransaction)
class PettyCashTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_date", "transaction_type", "title", "reference_no", "amount", "status")
    list_filter = ("transaction_type", "status")
    search_fields = ("title", "reference_no")
