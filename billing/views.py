from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal

from .forms import (
    CustomerForm,
    DeliveryNoteForm,
    FinanceEntryForm,
    InvoiceForm,
    MerchantForm,
    PettyCashTransactionForm,
    ProductForm,
    ProductionTaskForm,
    QuotationForm,
    RegisterForm,
    RefurbishmentJobForm,
    ReturnRMAForm,
    SalesOrderForm,
    StockMovementForm,
    UserProfileForm,
    WarehouseForm,
)
from .models import (
    AuditLog,
    Customer,
    DeliveryNote,
    FinanceEntry,
    Invoice,
    Merchant,
    PettyCashTransaction,
    Product,
    ProductionTask,
    Quotation,
    RefurbishmentJob,
    ReturnRMA,
    SalesOrder,
    StockMovement,
    UserProfile,
    Warehouse,
    WarehouseStock,
)

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "index")
        messages.error(request, "Invalid username or password.")

    users = UserProfile.objects.select_related("user").filter(status="Active", user__is_active=True).order_by("user__username")
    return render(request, "login.html", {"users": users})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            profile = form.save()
            login(request, profile.user)
            messages.success(request, "Registration complete.")
            return redirect("index")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def forgot_username_view(request):
    users = UserProfile.objects.select_related("user").filter(status="Active", user__is_active=True).order_by("user__username")
    return render(request, "forgot_username.html", {"users": users})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def index(request):
    active_finance = FinanceEntry.objects.filter(status="Active")
    investments = active_finance.filter(entry_type=FinanceEntry.INVESTMENT).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    withdrawals = active_finance.filter(entry_type=FinanceEntry.WITHDRAWAL).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    expenses = active_finance.filter(entry_type=FinanceEntry.EXPENSE).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    petty_add = PettyCashTransaction.objects.filter(status="Active", transaction_type=PettyCashTransaction.ADD).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    petty_minus = PettyCashTransaction.objects.filter(status="Active", transaction_type=PettyCashTransaction.MINUS).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    receivables = Invoice.objects.filter(status="Active").aggregate(total=Sum("amount"))["total"] or Decimal("0")
    payables = Merchant.objects.filter(status="Active").aggregate(total=Sum("payables"))["total"] or Decimal("0")
    stock_alerts = Product.objects.filter(status="Active", stock_quantity__lte=5).count()

    return render(request, "index.html", {
        "receivables": receivables,
        "payables": payables,
        "cash_balance": investments + petty_add - withdrawals - expenses - petty_minus,
        "petty_cash_balance": petty_add - petty_minus,
        "open_invoices": Invoice.objects.filter(status="Active").count(),
        "stock_alerts": stock_alerts,
        "production_open": RefurbishmentJob.objects.exclude(production_status=RefurbishmentJob.READY).count(),
        "returns_open": ReturnRMA.objects.exclude(approval_status=ReturnRMA.CLOSED).count(),
        "recent_invoices": Invoice.objects.select_related("customer")[:5],
        "recent_returns": ReturnRMA.objects.select_related("customer", "product")[:5],
        "recent_customers": Customer.objects.all()[:5],
    })


MODULES = {
    "warehouses": {
        "model": Warehouse,
        "form": WarehouseForm,
        "title": "Warehouses",
        "description": "Manage warehouse locations, responsible staff, and active status.",
        "breadcrumb": "Warehouses",
        "fields": [("Code", "code"), ("Name", "name"), ("Location", "location"), ("Manager", "manager_name"), ("Status", "status")],
    },
    "stock_movements": {
        "model": StockMovement,
        "form": StockMovementForm,
        "title": "Stock Movements",
        "description": "Receive, transfer, adjust, issue, and barcode-track stock.",
        "breadcrumb": "Stock Movements",
        "fields": [("Date", "movement_date"), ("Type", "movement_type"), ("Product", "product"), ("Qty", "quantity"), ("Reference", "reference_no"), ("Status", "status")],
    },
    "refurbishment_jobs": {
        "model": RefurbishmentJob,
        "form": RefurbishmentJobForm,
        "title": "Refurbishment Jobs",
        "description": "Track device intake, model status, supplier status, QC, and production progress.",
        "breadcrumb": "Refurbishment Jobs",
        "fields": [("Intake No.", "intake_no"), ("Model", "model_name"), ("Serial", "serial_no"), ("Technician", "qc_technician"), ("Production", "production_status"), ("Supplier Status", "supplier_status")],
    },
    "production_tasks": {
        "model": ProductionTask,
        "form": ProductionTaskForm,
        "title": "Production Tasks",
        "description": "Assign checking, repair, QC, and completion tasks to technicians.",
        "breadcrumb": "Production Tasks",
        "fields": [("Date", "task_date"), ("Job", "job"), ("Stage", "stage"), ("Assigned To", "assigned_to"), ("Issue", "issue_found"), ("Status", "status")],
    },
    "quotations": {
        "model": Quotation,
        "form": QuotationForm,
        "title": "Quotations",
        "description": "Create and approve customer quotations before sales orders.",
        "breadcrumb": "Quotations",
        "fields": [("Quote No.", "quotation_number"), ("Customer", "customer"), ("Date", "quotation_date"), ("Valid Until", "valid_until"), ("Amount", "amount"), ("Status", "status")],
        "actions": [("Create Order", "quotation_to_order")],
    },
    "sales_orders": {
        "model": SalesOrder,
        "form": SalesOrderForm,
        "title": "Sales Orders",
        "description": "Convert approved quotations into customer sales orders.",
        "breadcrumb": "Sales Orders",
        "fields": [("Order No.", "order_number"), ("Customer", "customer"), ("Quote", "quotation"), ("Order Date", "order_date"), ("Amount", "amount"), ("Status", "status")],
        "actions": [("Delivery Note", "sales_order_to_delivery"), ("Invoice", "sales_order_to_invoice")],
    },
    "delivery_notes": {
        "model": DeliveryNote,
        "form": DeliveryNoteForm,
        "title": "Delivery Notes",
        "description": "Track deliveries, dispatch references, and completion status.",
        "breadcrumb": "Delivery Notes",
        "fields": [("Delivery No.", "delivery_number"), ("Order", "sales_order"), ("Customer", "customer"), ("Date", "delivery_date"), ("Tracking", "tracking_no"), ("Status", "status")],
    },
    "returns": {
        "model": ReturnRMA,
        "form": ReturnRMAForm,
        "title": "Returns / RMA",
        "description": "Register returned devices, approve returns, and track repair or replacement.",
        "breadcrumb": "Returns / RMA",
        "fields": [("RMA No.", "rma_number"), ("Customer", "customer"), ("Product", "product"), ("Date", "return_date"), ("Reason", "reason"), ("Status", "approval_status")],
        "actions": [("Approve", "rma_approve"), ("Close", "rma_close")],
    },
    "users": {
        "model": UserProfile,
        "form": UserProfileForm,
        "title": "User Roles",
        "description": "Assign management, accountant, sales manager, and sales staff access profiles.",
        "breadcrumb": "User Roles",
        "fields": [("User", "user"), ("Role", "role"), ("Phone", "phone"), ("Status", "status")],
    },
}


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


def module_list(request, module):
    config = MODULES[module]
    records = config["model"].objects.all()
    rows = [
        {
            "record": record,
            "cells": [getattr(record, field_name) for _, field_name in config["fields"]],
        }
        for record in records
    ]
    return render(request, "records_list.html", {
        **config,
        "module": module,
        "records": records,
        "rows": rows,
        "new_url": f"{module}_new",
        "edit_url": f"{module}_edit",
        "delete_url": f"{module}_delete",
        "actions": config.get("actions", []),
    })


def module_form(request, module, pk=None):
    config = MODULES[module]
    model = config["model"]
    form_class = config["form"]
    record = get_object_or_404(model, pk=pk) if pk else None
    is_first_user_setup = module == "users" and record is None and not UserProfile.objects.exists()

    if request.method == "POST":
        form = form_class(request.POST, instance=record)
        if form.is_valid():
            saved = form.save()
            action = "updated" if record else "added"
            log_activity(request, config["title"], action.title(), saved)
            messages.success(request, f"{config['breadcrumb']} {action} successfully.")
            if is_first_user_setup:
                login(request, saved.user)
                return redirect("index")
            return redirect(module)
    else:
        form = form_class(instance=record)

    return render(request, "entity_form.html", {
        "form": form,
        "title": f"Edit {config['breadcrumb']}" if record else f"New {config['breadcrumb']}",
        "list_url": module,
        "breadcrumb": config["breadcrumb"],
    })


def module_delete(request, module, pk):
    config = MODULES[module]
    record = get_object_or_404(config["model"], pk=pk)
    if request.method == "POST":
        object_name = str(record)
        if module == "users":
            log_activity(request, config["title"], "Deleted", object_name)
            record.user.delete()
        else:
            record.delete()
            log_activity(request, config["title"], "Deleted", object_name)
        messages.success(request, f"{config['breadcrumb']} deleted successfully.")
        return redirect(module)

    return render(request, "confirm_delete.html", {
        "object": record,
        "title": f"Delete {config['breadcrumb']}",
        "list_url": module,
    })


def log_activity(request, module, action, obj):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        module=module,
        action=action,
        object_name=str(obj),
    )


def next_number(prefix, model, field_name):
    today = timezone.localdate().strftime("%Y%m%d")
    base = f"{prefix}-{today}"
    count = model.objects.filter(**{f"{field_name}__startswith": base}).count() + 1
    return f"{base}-{count:03d}"


def quotation_to_order(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    order = SalesOrder.objects.create(
        order_number=next_number("SO", SalesOrder, "order_number"),
        quotation=quotation,
        customer=quotation.customer,
        order_date=timezone.localdate(),
        expected_delivery_date=quotation.valid_until,
        amount=quotation.amount,
        status="Pending",
        notes=f"Created from quotation {quotation.quotation_number}.",
    )
    quotation.status = "Approved"
    quotation.save(update_fields=["status"])
    log_activity(request, "Sales Orders", "Created From Quotation", order)
    messages.success(request, f"Sales order {order.order_number} created from quotation.")
    return redirect("sales_orders")


def sales_order_to_delivery(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    delivery = DeliveryNote.objects.create(
        delivery_number=next_number("DN", DeliveryNote, "delivery_number"),
        sales_order=order,
        customer=order.customer,
        delivery_date=timezone.localdate(),
        status="Pending",
        notes=f"Created from sales order {order.order_number}.",
    )
    order.status = "Approved"
    order.save(update_fields=["status"])
    log_activity(request, "Delivery Notes", "Created From Sales Order", delivery)
    messages.success(request, f"Delivery note {delivery.delivery_number} created.")
    return redirect("delivery_notes")


def sales_order_to_invoice(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    invoice_obj = Invoice.objects.create(
        invoice_number=next_number("INV", Invoice, "invoice_number"),
        customer=order.customer,
        invoice_date=timezone.localdate(),
        due_date=order.expected_delivery_date,
        amount=order.amount,
        status="Active",
        notes=f"Created from sales order {order.order_number}.",
    )
    order.status = "Completed"
    order.save(update_fields=["status"])
    log_activity(request, "Invoice", "Created From Sales Order", invoice_obj)
    messages.success(request, f"Invoice {invoice_obj.invoice_number} created.")
    return redirect("invoice_preview", pk=invoice_obj.pk)


def rma_approve(request, pk):
    rma = get_object_or_404(ReturnRMA, pk=pk)
    rma.approval_status = ReturnRMA.APPROVED
    rma.save(update_fields=["approval_status"])
    log_activity(request, "Returns / RMA", "Approved", rma)
    messages.success(request, f"RMA {rma.rma_number} approved.")
    return redirect("returns")


def rma_close(request, pk):
    rma = get_object_or_404(ReturnRMA, pk=pk)
    rma.approval_status = ReturnRMA.CLOSED
    rma.closed_date = timezone.localdate()
    rma.save(update_fields=["approval_status", "closed_date"])
    log_activity(request, "Returns / RMA", "Closed", rma)
    messages.success(request, f"RMA {rma.rma_number} closed.")
    return redirect("returns")

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


def reports(request):
    production_by_status = RefurbishmentJob.objects.values("production_status").annotate(total=Count("id")).order_by("production_status")
    returns_by_status = ReturnRMA.objects.values("approval_status").annotate(total=Count("id")).order_by("approval_status")
    stock_by_category = Product.objects.values("category").annotate(total_quantity=Sum("stock_quantity")).order_by("category")
    sales_total = Invoice.objects.filter(status="Active").aggregate(total=Sum("amount"))["total"] or Decimal("0")
    quote_total = Quotation.objects.exclude(status="Cancelled").aggregate(total=Sum("amount"))["total"] or Decimal("0")

    return render(request, "reports.html", {
        "inventory_count": Product.objects.count(),
        "warehouse_count": Warehouse.objects.count(),
        "warehouse_stock_count": WarehouseStock.objects.count(),
        "stock_movements_count": StockMovement.objects.count(),
        "production_count": RefurbishmentJob.objects.count(),
        "sales_total": sales_total,
        "quote_total": quote_total,
        "returns_count": ReturnRMA.objects.count(),
        "production_by_status": production_by_status,
        "returns_by_status": returns_by_status,
        "stock_by_category": stock_by_category,
    })


def audit_logs(request):
    logs = AuditLog.objects.select_related("user")[:100]
    return render(request, "audit_logs.html", {"logs": logs})


def warehouse_stock(request):
    balances = WarehouseStock.objects.select_related("warehouse", "product")
    return render(request, "warehouse_stock.html", {"balances": balances})
