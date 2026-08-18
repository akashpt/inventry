from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal

from .forms import CustomerForm, FinanceEntryForm, InvoiceForm, MerchantForm, PettyCashTransactionForm, ProductForm
from .models import Customer, FinanceEntry, Invoice, Merchant, PettyCashTransaction, Product

# Create your views here.

def index(request):
    return render(request, "index.html")


def customer(request):
    customers = Customer.objects.all()
    return render(request, "customer.html", {"customers": customers})


def newcustomer(request):
    return customer_form(request)


def customer_form(request, pk=None):
    customer_obj = get_object_or_404(Customer, pk=pk) if pk else None
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer_obj)
        if form.is_valid():
            form.save()
            message = "Customer updated successfully." if customer_obj else "Customer added successfully."
            messages.success(request, message)
            return redirect("customer")
    else:
        form = CustomerForm(instance=customer_obj)

    return render(request, "entity_form.html", {
        "form": form,
        "title": "Edit Customer" if customer_obj else "New Customer",
        "list_url": "customer",
        "breadcrumb": "Customers",
    })


def customer_delete(request, pk):
    customer_obj = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer_obj.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect("customer")

    return render(request, "confirm_delete.html", {
        "object": customer_obj,
        "title": "Delete Customer",
        "list_url": "customer",
    })

def merchant(request):
    merchants = Merchant.objects.all()
    return render(request, "merchant.html", {"merchants": merchants})

def newmerchant(request):
    return merchant_form(request)


def merchant_form(request, pk=None):
    merchant_obj = get_object_or_404(Merchant, pk=pk) if pk else None
    if request.method == "POST":
        form = MerchantForm(request.POST, instance=merchant_obj)
        if form.is_valid():
            form.save()
            message = "Merchant updated successfully." if merchant_obj else "Merchant added successfully."
            messages.success(request, message)
            return redirect("merchant")
    else:
        form = MerchantForm(instance=merchant_obj)

    return render(request, "entity_form.html", {
        "form": form,
        "title": "Edit Merchant" if merchant_obj else "New Merchant",
        "list_url": "merchant",
        "breadcrumb": "Merchant",
    })


def merchant_delete(request, pk):
    merchant_obj = get_object_or_404(Merchant, pk=pk)
    if request.method == "POST":
        merchant_obj.delete()
        messages.success(request, "Merchant deleted successfully.")
        return redirect("merchant")

    return render(request, "confirm_delete.html", {
        "object": merchant_obj,
        "title": "Delete Merchant",
        "list_url": "merchant",
    })

def products(request):
    products_list = Product.objects.all()
    return render(request, "products.html", {"products": products_list})


def product_form(request, pk=None):
    product_obj = get_object_or_404(Product, pk=pk) if pk else None
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product_obj)
        if form.is_valid():
            form.save()
            message = "Product updated successfully." if product_obj else "Product added successfully."
            messages.success(request, message)
            return redirect("products")
    else:
        form = ProductForm(instance=product_obj)

    return render(request, "entity_form.html", {
        "form": form,
        "title": "Edit Product" if product_obj else "New Product",
        "list_url": "products",
        "breadcrumb": "Products",
    })


def product_delete(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product_obj.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("products")

    return render(request, "confirm_delete.html", {
        "object": product_obj,
        "title": "Delete Product",
        "list_url": "products",
    })

def invoice(request):
    invoices = Invoice.objects.select_related("customer")
    return render(request, "invoice.html", {"invoices": invoices})


def invoice_form(request, pk=None):
    invoice_obj = get_object_or_404(Invoice, pk=pk) if pk else None
    is_edit = invoice_obj is not None
    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice_obj)
        if form.is_valid():
            invoice_obj = form.save()
            message = "Invoice updated successfully." if is_edit else "Invoice added successfully."
            messages.success(request, message)
            return redirect("invoice_preview", pk=invoice_obj.pk)
    else:
        form = InvoiceForm(instance=invoice_obj)

    return render(request, "entity_form.html", {
        "form": form,
        "title": "Edit Invoice" if invoice_obj else "New Invoice",
        "list_url": "invoice",
        "breadcrumb": "Invoice",
    })


def invoice_delete(request, pk):
    invoice_obj = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        invoice_obj.delete()
        messages.success(request, "Invoice deleted successfully.")
        return redirect("invoice")

    return render(request, "confirm_delete.html", {
        "object": invoice_obj,
        "title": "Delete Invoice",
        "list_url": "invoice",
    })


def invoice_preview(request, pk):
    invoice_obj = get_object_or_404(Invoice.objects.select_related("customer"), pk=pk)
    vat_rate = Decimal("0.05")
    subtotal = invoice_obj.amount
    vat_amount = subtotal * vat_rate
    total = subtotal + vat_amount

    return render(request, "invoice_preview.html", {
        "invoice_item": invoice_obj,
        "subtotal": subtotal,
        "vat_amount": vat_amount,
        "total": total,
    })


def finance_entries(request, entry_type):
    entries = FinanceEntry.objects.filter(entry_type=entry_type)
    return render(request, "finance_entries.html", {
        "entries": entries,
        "entry_type": entry_type,
        "title": f"{entry_type} List",
        "new_url": finance_url_name(entry_type, "new"),
    })


def finance_entry_form(request, entry_type, pk=None):
    entry_obj = get_object_or_404(FinanceEntry, pk=pk, entry_type=entry_type) if pk else None
    if request.method == "POST":
        form = FinanceEntryForm(request.POST, instance=entry_obj)
        if form.is_valid():
            finance_obj = form.save(commit=False)
            finance_obj.entry_type = entry_type
            finance_obj.save()
            message = f"{entry_type} updated successfully." if entry_obj else f"{entry_type} added successfully."
            messages.success(request, message)
            return redirect(finance_url_name(entry_type, "list"))
    else:
        form = FinanceEntryForm(instance=entry_obj)

    return render(request, "entity_form.html", {
        "form": form,
        "title": f"Edit {entry_type}" if entry_obj else f"New {entry_type}",
        "list_url": finance_url_name(entry_type, "list"),
        "breadcrumb": entry_type,
    })


def finance_entry_delete(request, entry_type, pk):
    entry_obj = get_object_or_404(FinanceEntry, pk=pk, entry_type=entry_type)
    if request.method == "POST":
        entry_obj.delete()
        messages.success(request, f"{entry_type} deleted successfully.")
        return redirect(finance_url_name(entry_type, "list"))

    return render(request, "confirm_delete.html", {
        "object": entry_obj,
        "title": f"Delete {entry_type}",
        "list_url": finance_url_name(entry_type, "list"),
    })


def investment(request):
    return finance_entries(request, FinanceEntry.INVESTMENT)


def investment_new(request):
    return finance_entry_form(request, FinanceEntry.INVESTMENT)


def investment_edit(request, pk):
    return finance_entry_form(request, FinanceEntry.INVESTMENT, pk)


def investment_delete(request, pk):
    return finance_entry_delete(request, FinanceEntry.INVESTMENT, pk)


def withdrawal(request):
    return finance_entries(request, FinanceEntry.WITHDRAWAL)


def withdrawal_new(request):
    return finance_entry_form(request, FinanceEntry.WITHDRAWAL)


def withdrawal_edit(request, pk):
    return finance_entry_form(request, FinanceEntry.WITHDRAWAL, pk)


def withdrawal_delete(request, pk):
    return finance_entry_delete(request, FinanceEntry.WITHDRAWAL, pk)


def expenses(request):
    return finance_entries(request, FinanceEntry.EXPENSE)


def expense_new(request):
    return finance_entry_form(request, FinanceEntry.EXPENSE)


def expense_edit(request, pk):
    return finance_entry_form(request, FinanceEntry.EXPENSE, pk)


def expense_delete(request, pk):
    return finance_entry_delete(request, FinanceEntry.EXPENSE, pk)


def finance_url_name(entry_type, action):
    names = {
        FinanceEntry.INVESTMENT: {
            "list": "investment",
            "new": "investment_new",
            "edit": "investment_edit",
            "delete": "investment_delete",
        },
        FinanceEntry.WITHDRAWAL: {
            "list": "withdrawal",
            "new": "withdrawal_new",
            "edit": "withdrawal_edit",
            "delete": "withdrawal_delete",
        },
        FinanceEntry.EXPENSE: {
            "list": "expenses",
            "new": "expense_new",
            "edit": "expense_edit",
            "delete": "expense_delete",
        },
    }
    return names[entry_type][action]


def petty_cash(request):
    transactions = PettyCashTransaction.objects.all()
    active_transactions = transactions.filter(status="Active")
    total_added = sum(item.amount for item in active_transactions if item.transaction_type == PettyCashTransaction.ADD)
    total_minus = sum(item.amount for item in active_transactions if item.transaction_type == PettyCashTransaction.MINUS)
    balance = total_added - total_minus

    return render(request, "petty_cash.html", {
        "transactions": transactions,
        "total_added": total_added,
        "total_minus": total_minus,
        "balance": balance,
    })


def petty_cash_form(request, pk=None):
    transaction_obj = get_object_or_404(PettyCashTransaction, pk=pk) if pk else None
    if request.method == "POST":
        form = PettyCashTransactionForm(request.POST, instance=transaction_obj)
        if form.is_valid():
            form.save()
            message = "Petty cash transaction updated successfully." if transaction_obj else "Petty cash transaction added successfully."
            messages.success(request, message)
            return redirect("petty_cash")
    else:
        form = PettyCashTransactionForm(instance=transaction_obj)

    return render(request, "entity_form.html", {
        "form": form,
        "title": "Edit Petty Cash" if transaction_obj else "New Petty Cash",
        "list_url": "petty_cash",
        "breadcrumb": "Petty Cash",
    })


def petty_cash_delete(request, pk):
    transaction_obj = get_object_or_404(PettyCashTransaction, pk=pk)
    if request.method == "POST":
        transaction_obj.delete()
        messages.success(request, "Petty cash transaction deleted successfully.")
        return redirect("petty_cash")

    return render(request, "confirm_delete.html", {
        "object": transaction_obj,
        "title": "Delete Petty Cash",
        "list_url": "petty_cash",
    })
