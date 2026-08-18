from django import forms

from .models import Customer, FinanceEntry, Invoice, Merchant, PettyCashTransaction, Product


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_type",
            "salutation",
            "first_name",
            "last_name",
            "company_name",
            "display_name",
            "display_name_secondary",
            "email",
            "work_phone",
            "mobile",
            "language",
            "currency",
            "payment_terms",
            "portal_enabled",
            "street_address",
            "city",
            "state",
            "postal_code",
            "country",
            "remarks",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class MerchantForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = [
            "merchant_type",
            "salutation",
            "first_name",
            "last_name",
            "company_name",
            "display_name",
            "display_name_secondary",
            "email",
            "work_phone",
            "mobile",
            "language",
            "currency",
            "payment_terms",
            "portal_enabled",
            "street_address",
            "city",
            "state",
            "postal_code",
            "country",
            "remarks",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "unit",
            "sale_price",
            "purchase_price",
            "stock_quantity",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "customer",
            "invoice_date",
            "due_date",
            "amount",
            "status",
            "notes",
        ]
        widgets = {
            "invoice_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class FinanceEntryForm(forms.ModelForm):
    class Meta:
        model = FinanceEntry
        fields = [
            "entry_date",
            "title",
            "party_name",
            "payment_mode",
            "reference_no",
            "amount",
            "status",
            "notes",
        ]
        widgets = {
            "entry_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class PettyCashTransactionForm(forms.ModelForm):
    class Meta:
        model = PettyCashTransaction
        fields = [
            "transaction_date",
            "transaction_type",
            "title",
            "reference_no",
            "amount",
            "status",
            "notes",
        ]
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


def apply_bootstrap_widgets(form):
    for field in form.fields.values():
        css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
        if isinstance(field.widget, forms.Select):
            css_class = "form-select"
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} {css_class}".strip()
