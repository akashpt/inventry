from django import forms
from django.contrib.auth import get_user_model

from .models import (
    Customer,
    DeliveryNote,
    DeliveryNoteItem,
    FinanceEntry,
    Invoice,
    InvoiceItem,
    Merchant,
    AppSetting,
    PettyCashTransaction,
    PaymentReceived,
    Product,
    ProductionTask,
    PurchaseOrder,
    PurchaseOrderItem,
    Quotation,
    QuotationItem,
    RefurbishmentJob,
    ReturnRMA,
    ReturnHistory,
    SalesOrder,
    SalesOrderItem,
    STATUS_CHOICES,
    StockMovement,
    SupplierBill,
    UserProfile,
    Warehouse,
)


User = get_user_model()


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
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "code", "location", "manager_name", "status", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "movement_date",
            "movement_type",
            "product",
            "quantity",
            "from_warehouse",
            "to_warehouse",
            "reference_no",
            "barcode",
            "status",
            "notes",
        ]
        widgets = {
            "movement_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity == 0:
            raise forms.ValidationError("Quantity cannot be zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get("movement_type")
        quantity = cleaned_data.get("quantity")
        from_warehouse = cleaned_data.get("from_warehouse")
        to_warehouse = cleaned_data.get("to_warehouse")

        if movement_type != StockMovement.ADJUSTMENT and quantity is not None and quantity < 0:
            self.add_error("quantity", "Only stock adjustments can use a negative quantity.")
        if movement_type == StockMovement.RECEIVE and not to_warehouse:
            self.add_error("to_warehouse", "Select the receiving warehouse.")
        if movement_type == StockMovement.ISSUE and not from_warehouse:
            self.add_error("from_warehouse", "Select the issuing warehouse.")
        if movement_type == StockMovement.TRANSFER:
            if not from_warehouse:
                self.add_error("from_warehouse", "Select the source warehouse.")
            if not to_warehouse:
                self.add_error("to_warehouse", "Select the destination warehouse.")
            if from_warehouse and to_warehouse and from_warehouse == to_warehouse:
                self.add_error("to_warehouse", "Destination must be different from source.")
        if movement_type == StockMovement.ADJUSTMENT and not (from_warehouse or to_warehouse):
            self.add_error("to_warehouse", "Select a warehouse for the adjustment.")
        return cleaned_data


class RefurbishmentJobForm(forms.ModelForm):
    class Meta:
        model = RefurbishmentJob
        fields = [
            "intake_no",
            "supplier",
            "model_name",
            "serial_no",
            "configuration",
            "intake_date",
            "qc_technician",
            "supplier_status",
            "production_status",
            "finished_product",
            "finished_warehouse",
            "estimated_cost",
            "actual_cost",
            "notes",
        ]
        widgets = {
            "intake_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class ProductionTaskForm(forms.ModelForm):
    class Meta:
        model = ProductionTask
        fields = [
            "job",
            "task_date",
            "stage",
            "assigned_to",
            "issue_found",
            "repair_action",
            "parts_used",
            "parts_product",
            "parts_warehouse",
            "parts_quantity",
            "status",
        ]
        widgets = {
            "task_date": forms.DateInput(attrs={"type": "date"}),
        }

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


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ["quotation_number", "customer", "quotation_date", "valid_until", "amount", "status", "notes"]
        widgets = {
            "quotation_date": forms.DateInput(attrs={"type": "date"}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["quotation", "product", "description", "quantity", "unit_price", "discount_amount", "tax_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = [
            "order_number",
            "quotation",
            "customer",
            "order_date",
            "expected_delivery_date",
            "amount",
            "status",
            "notes",
        ]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "expected_delivery_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class SalesOrderItemForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ["sales_order", "product", "warehouse", "description", "quantity", "unit_price", "discount_amount", "tax_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class DeliveryNoteForm(forms.ModelForm):
    class Meta:
        model = DeliveryNote
        fields = [
            "delivery_number",
            "sales_order",
            "customer",
            "delivery_date",
            "delivered_by",
            "tracking_no",
            "status",
            "notes",
        ]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class DeliveryNoteItemForm(forms.ModelForm):
    class Meta:
        model = DeliveryNoteItem
        fields = ["delivery_note", "product", "warehouse", "quantity", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["invoice", "product", "warehouse", "description", "quantity", "unit_price", "discount_amount", "tax_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["order_number", "supplier", "order_date", "expected_date", "status", "notes"]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "expected_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["purchase_order", "product", "warehouse", "quantity", "unit_price", "tax_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity


class SupplierBillForm(forms.ModelForm):
    class Meta:
        model = SupplierBill
        fields = ["bill_number", "supplier", "purchase_order", "bill_date", "due_date", "amount", "paid_amount", "status", "notes"]
        widgets = {
            "bill_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class PaymentReceivedForm(forms.ModelForm):
    class Meta:
        model = PaymentReceived
        fields = ["payment_number", "customer", "invoice", "payment_date", "amount", "payment_mode", "reference_no", "notes"]
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class AppSettingForm(forms.ModelForm):
    class Meta:
        model = AppSetting
        fields = ["company_name", "currency", "low_stock_threshold", "vat_rate", "default_warehouse"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class ReturnRMAForm(forms.ModelForm):
    class Meta:
        model = ReturnRMA
        fields = [
            "rma_number",
            "customer",
            "invoice",
            "product",
            "return_date",
            "reason",
            "approval_status",
            "resolution",
            "assigned_to",
            "closed_date",
            "notes",
        ]
        widgets = {
            "return_date": forms.DateInput(attrs={"type": "date"}),
            "closed_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widgets(self)


class UserProfileForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    phone = forms.CharField(max_length=30, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        if self.instance:
            user = self.instance.user
            self.fields["password"].help_text = "Leave blank to keep the current password."
            self.initial.update({
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": self.instance.role,
                "phone": self.instance.phone,
                "status": self.instance.status,
                "is_active": user.is_active,
            })
        else:
            self.fields["password"].required = True
        apply_bootstrap_widgets(self)

    def clean_username(self):
        username = self.cleaned_data["username"]
        query = User.objects.filter(username=username)
        if self.instance:
            query = query.exclude(pk=self.instance.user_id)
        if query.exists():
            raise forms.ValidationError("This username is already used.")
        return username

    def save(self):
        if self.instance:
            profile = self.instance
            user = profile.user
        else:
            user = User()
            profile = UserProfile(user=user)

        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.is_active = self.cleaned_data["is_active"]
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        user.save()

        profile.role = self.cleaned_data["role"]
        profile.phone = self.cleaned_data["phone"]
        profile.status = self.cleaned_data["status"]
        profile.save()
        return profile


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if UserProfile.objects.filter(role=UserProfile.MANAGEMENT, status="Active").exists():
            self.fields["role"].choices = [(UserProfile.SALES_STAFF, "Sales Staff")]
        apply_bootstrap_widgets(self)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already used.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            is_active=True,
        )
        profile = UserProfile.objects.create(
            user=user,
            role=self.cleaned_data["role"],
            status="Active",
        )
        return profile


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
