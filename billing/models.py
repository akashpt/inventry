from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


STATUS_CHOICES = [
    ("Active", "Active"),
    ("Inactive", "Inactive"),
]

DOCUMENT_STATUS_CHOICES = [
    ("Draft", "Draft"),
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
]


class Customer(models.Model):
    BUSINESS = "Business"
    INDIVIDUAL = "Individual"

    customer_type = models.CharField(max_length=20, default=BUSINESS)
    salutation = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    display_name = models.CharField(max_length=150)
    display_name_secondary = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    work_phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    language = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=50, blank=True)
    portal_enabled = models.BooleanField(default=False)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    receivables = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.display_name


class Merchant(models.Model):
    merchant_type = models.CharField(max_length=20, default="Business")
    salutation = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    display_name = models.CharField(max_length=150)
    display_name_secondary = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    work_phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    language = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=50, blank=True)
    portal_enabled = models.BooleanField(default=False)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    payables = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.display_name


class Product(models.Model):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=30, default="pcs", blank=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    location = models.CharField(max_length=180, blank=True)
    manager_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["warehouse__name", "product__name"]
        unique_together = ("warehouse", "product")

    def __str__(self):
        return f"{self.warehouse} - {self.product}: {self.quantity}"


class StockMovement(models.Model):
    RECEIVE = "Receive"
    TRANSFER = "Transfer"
    ADJUSTMENT = "Adjustment"
    ISSUE = "Issue"

    MOVEMENT_TYPE_CHOICES = [
        (RECEIVE, "Stock Receiving"),
        (TRANSFER, "Stock Transfer"),
        (ADJUSTMENT, "Stock Adjustment"),
        (ISSUE, "Stock Issue"),
    ]

    movement_date = models.DateField()
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_out")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_in")
    reference_no = models.CharField(max_length=80, blank=True)
    barcode = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=30, choices=DOCUMENT_STATUS_CHOICES, default="Completed")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-movement_date", "-created_at"]

    @property
    def signed_quantity(self):
        return self.quantity if self.movement_type in [self.RECEIVE, self.ADJUSTMENT] else -self.quantity

    def clean(self):
        if self.movement_type == self.RECEIVE and not self.to_warehouse:
            raise ValidationError({"to_warehouse": "Receiving stock requires a destination warehouse."})
        if self.movement_type == self.ISSUE and not self.from_warehouse:
            raise ValidationError({"from_warehouse": "Issuing stock requires a source warehouse."})
        if self.movement_type == self.TRANSFER:
            if not self.from_warehouse or not self.to_warehouse:
                raise ValidationError("Stock transfer requires both source and destination warehouses.")
            if self.from_warehouse == self.to_warehouse:
                raise ValidationError("Source and destination warehouses must be different.")
        if self.movement_type == self.ADJUSTMENT and not (self.from_warehouse or self.to_warehouse):
            raise ValidationError("Stock adjustment requires at least one warehouse.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous = None
            if self.pk:
                previous = StockMovement.objects.select_for_update().get(pk=self.pk)
            self.full_clean()
            super().save(*args, **kwargs)
            if previous:
                previous.apply_stock(reverse=True)
            self.apply_stock()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.apply_stock(reverse=True)
            super().delete(*args, **kwargs)

    def apply_stock(self, reverse=False):
        if self.status != "Completed":
            return
        multiplier = -1 if reverse else 1
        quantity = self.quantity * multiplier

        if self.movement_type == self.RECEIVE:
            adjust_stock(self.product, self.to_warehouse, quantity)
        elif self.movement_type == self.ISSUE:
            adjust_stock(self.product, self.from_warehouse, -quantity)
        elif self.movement_type == self.TRANSFER:
            adjust_stock(self.product, self.from_warehouse, -quantity, update_product=False)
            adjust_stock(self.product, self.to_warehouse, quantity, update_product=False)
        elif self.movement_type == self.ADJUSTMENT:
            warehouse = self.to_warehouse or self.from_warehouse
            adjust_stock(self.product, warehouse, quantity)

    def __str__(self):
        return f"{self.movement_type} - {self.product}"


def adjust_stock(product, warehouse, quantity, update_product=True):
    stock, _ = WarehouseStock.objects.select_for_update().get_or_create(
        product=product,
        warehouse=warehouse,
        defaults={"quantity": 0},
    )
    stock.quantity += quantity
    stock.save(update_fields=["quantity", "updated_at"])
    if update_product:
        Product.objects.filter(pk=product.pk).update(stock_quantity=models.F("stock_quantity") + quantity)


class RefurbishmentJob(models.Model):
    INTAKE = "Intake"
    CHECKING = "Checking"
    REPAIR = "Repair"
    QC = "QC"
    READY = "Ready"
    SCRAP = "Scrap"

    STATUS_CHOICES = [
        (INTAKE, "Device Intake"),
        (CHECKING, "Checking"),
        (REPAIR, "Repair"),
        (QC, "QC"),
        (READY, "Ready for Sale"),
        (SCRAP, "Scrap"),
    ]

    intake_no = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.CharField(max_length=150)
    serial_no = models.CharField(max_length=120, blank=True)
    configuration = models.CharField(max_length=255, blank=True)
    intake_date = models.DateField()
    qc_technician = models.CharField(max_length=120, blank=True)
    supplier_status = models.CharField(max_length=120, blank=True)
    production_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=INTAKE)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-intake_date", "-created_at"]

    def __str__(self):
        return f"{self.intake_no} - {self.model_name}"


class ProductionTask(models.Model):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    HOLD = "Hold"

    TASK_STATUS_CHOICES = [
        (OPEN, "Open"),
        (IN_PROGRESS, "In Progress"),
        (DONE, "Done"),
        (HOLD, "Hold"),
    ]

    job = models.ForeignKey(RefurbishmentJob, on_delete=models.CASCADE, related_name="tasks")
    task_date = models.DateField()
    stage = models.CharField(max_length=80)
    assigned_to = models.CharField(max_length=120, blank=True)
    issue_found = models.CharField(max_length=255, blank=True)
    repair_action = models.TextField(blank=True)
    parts_used = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, choices=TASK_STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-task_date", "-created_at"]

    def __str__(self):
        return f"{self.job} - {self.stage}"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-invoice_date", "-created_at"]

    def __str__(self):
        return self.invoice_number


class Quotation(models.Model):
    quotation_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    quotation_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=DOCUMENT_STATUS_CHOICES, default="Draft")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-quotation_date", "-created_at"]

    def __str__(self):
        return self.quotation_number


class SalesOrder(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=DOCUMENT_STATUS_CHOICES, default="Pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_date", "-created_at"]

    def __str__(self):
        return self.order_number


class DeliveryNote(models.Model):
    delivery_number = models.CharField(max_length=50, unique=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_date = models.DateField()
    delivered_by = models.CharField(max_length=120, blank=True)
    tracking_no = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=DOCUMENT_STATUS_CHOICES, default="Pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-delivery_date", "-created_at"]

    def __str__(self):
        return self.delivery_number


class ReturnRMA(models.Model):
    REQUESTED = "Requested"
    APPROVED = "Approved"
    REPAIR = "Repair"
    REPLACEMENT = "Replacement"
    CLOSED = "Closed"
    REJECTED = "Rejected"

    RMA_STATUS_CHOICES = [
        (REQUESTED, "Requested"),
        (APPROVED, "Approved"),
        (REPAIR, "Repair"),
        (REPLACEMENT, "Replacement"),
        (CLOSED, "Closed"),
        (REJECTED, "Rejected"),
    ]

    rma_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    return_date = models.DateField()
    reason = models.CharField(max_length=255)
    approval_status = models.CharField(max_length=30, choices=RMA_STATUS_CHOICES, default=REQUESTED)
    resolution = models.CharField(max_length=120, blank=True)
    assigned_to = models.CharField(max_length=120, blank=True)
    closed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-return_date", "-created_at"]

    def __str__(self):
        return self.rma_number


class UserProfile(models.Model):
    MANAGEMENT = "Management"
    ACCOUNTANT = "Accountant"
    SALES_MANAGER = "Sales Manager"
    SALES_STAFF = "Sales Staff"

    ROLE_CHOICES = [
        (MANAGEMENT, "Management Full Access"),
        (ACCOUNTANT, "Accountant"),
        (SALES_MANAGER, "Sales Manager"),
        (SALES_STAFF, "Sales Staff"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default=SALES_STAFF)
    phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user} - {self.role}"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=120)
    module = models.CharField(max_length=80)
    object_name = models.CharField(max_length=150, blank=True)
    activity_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-activity_date"]

    def __str__(self):
        return f"{self.module} - {self.action}"


class FinanceEntry(models.Model):
    INVESTMENT = "Investment"
    WITHDRAWAL = "Withdrawal"
    EXPENSE = "Expense"

    ENTRY_TYPE_CHOICES = [
        (INVESTMENT, "Investment"),
        (WITHDRAWAL, "Withdrawal"),
        (EXPENSE, "Expense"),
    ]

    entry_type = models.CharField(max_length=30, choices=ENTRY_TYPE_CHOICES)
    entry_date = models.DateField()
    title = models.CharField(max_length=150)
    party_name = models.CharField(max_length=150, blank=True)
    payment_mode = models.CharField(max_length=50, blank=True)
    reference_no = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date", "-created_at"]

    def __str__(self):
        return f"{self.entry_type} - {self.title}"


class PettyCashTransaction(models.Model):
    ADD = "Add"
    MINUS = "Minus"

    TRANSACTION_TYPE_CHOICES = [
        (ADD, "Add Amount"),
        (MINUS, "Minus Amount"),
    ]

    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    title = models.CharField(max_length=150)
    reference_no = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]

    @property
    def signed_amount(self):
        return self.amount if self.transaction_type == self.ADD else -self.amount

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.title}"
