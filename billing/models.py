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

    def recalculate_stock(self):
        total = WarehouseStock.objects.filter(product=self).aggregate(total=models.Sum("quantity"))["total"] or 0
        self.stock_quantity = total
        self.save(update_fields=["stock_quantity"])


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
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
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
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="stock_out")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="stock_in")
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
    new_quantity = stock.quantity + quantity
    if new_quantity < 0:
        raise ValidationError(f"Not enough stock for {product} in {warehouse}.")
    stock.quantity = new_quantity
    stock.save(update_fields=["quantity", "updated_at"])
    if update_product:
        Product.objects.filter(pk=product.pk).update(stock_quantity=models.F("stock_quantity") + quantity)


def line_total(quantity, unit_price, discount_amount=0, tax_amount=0):
    return (quantity * unit_price) - discount_amount + tax_amount


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
    finished_product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True, related_name="refurbished_jobs")
    finished_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="refurbished_jobs")
    finished_stocked = models.BooleanField(default=False)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-intake_date", "-created_at"]

    def __str__(self):
        return f"{self.intake_no} - {self.model_name}"

    def save(self, *args, **kwargs):
        creating_stock = (
            self.production_status == self.READY
            and self.finished_product
            and self.finished_warehouse
            and not self.finished_stocked
        )
        with transaction.atomic():
            super().save(*args, **kwargs)
            if creating_stock:
                StockMovement.objects.create(
                    movement_date=self.intake_date,
                    movement_type=StockMovement.RECEIVE,
                    product=self.finished_product,
                    quantity=1,
                    to_warehouse=self.finished_warehouse,
                    reference_no=self.intake_no,
                    barcode=self.serial_no,
                    status="Completed",
                    notes="Auto-stocked from completed refurbishment job.",
                )
                self.finished_stocked = True
                super().save(update_fields=["finished_stocked"])


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
    parts_product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True, related_name="production_usage")
    parts_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="production_usage")
    parts_quantity = models.PositiveIntegerField(default=0)
    parts_issued = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=TASK_STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-task_date", "-created_at"]

    def __str__(self):
        return f"{self.job} - {self.stage}"

    def save(self, *args, **kwargs):
        issue_parts = (
            self.status == self.DONE
            and self.parts_product
            and self.parts_warehouse
            and self.parts_quantity
            and not self.parts_issued
        )
        with transaction.atomic():
            super().save(*args, **kwargs)
            if issue_parts:
                StockMovement.objects.create(
                    movement_date=self.task_date,
                    movement_type=StockMovement.ISSUE,
                    product=self.parts_product,
                    quantity=self.parts_quantity,
                    from_warehouse=self.parts_warehouse,
                    reference_no=str(self.job.intake_no),
                    status="Completed",
                    notes=f"Auto-issued for production task {self.stage}.",
                )
                self.parts_issued = True
                super().save(update_fields=["parts_issued"])


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Active")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-invoice_date", "-created_at"]

    def __str__(self):
        return self.invoice_number

    @property
    def balance_due(self):
        return self.amount - self.paid_amount


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

    def recalculate_amount(self):
        self.amount = self.items.aggregate(total=models.Sum("total"))["total"] or 0
        self.save(update_fields=["amount"])


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.total = line_total(self.quantity, self.unit_price, self.discount_amount, self.tax_amount)
        super().save(*args, **kwargs)
        self.quotation.recalculate_amount()

    def delete(self, *args, **kwargs):
        quotation = self.quotation
        super().delete(*args, **kwargs)
        quotation.recalculate_amount()

    def __str__(self):
        return f"{self.quotation} - {self.product}"


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

    def recalculate_amount(self):
        self.amount = self.items.aggregate(total=models.Sum("total"))["total"] or 0
        self.save(update_fields=["amount"])


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def clean(self):
        if self.warehouse:
            available = WarehouseStock.objects.filter(product=self.product, warehouse=self.warehouse).first()
            if not available or available.quantity < self.quantity:
                raise ValidationError("Selected warehouse does not have enough stock.")

    def save(self, *args, **kwargs):
        self.full_clean()
        self.total = line_total(self.quantity, self.unit_price, self.discount_amount, self.tax_amount)
        super().save(*args, **kwargs)
        self.sales_order.recalculate_amount()

    def delete(self, *args, **kwargs):
        sales_order = self.sales_order
        super().delete(*args, **kwargs)
        sales_order.recalculate_amount()

    def __str__(self):
        return f"{self.sales_order} - {self.product}"


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


class DeliveryNoteItem(models.Model):
    delivery_note = models.ForeignKey(DeliveryNote, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.delivery_note} - {self.product}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.total = line_total(self.quantity, self.unit_price, self.discount_amount, self.tax_amount)
        super().save(*args, **kwargs)
        self.invoice.amount = self.invoice.items.aggregate(total=models.Sum("total"))["total"] or 0
        self.invoice.save(update_fields=["amount"])

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.amount = invoice.items.aggregate(total=models.Sum("total"))["total"] or 0
        invoice.save(update_fields=["amount"])

    def __str__(self):
        return f"{self.invoice} - {self.product}"


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Merchant, on_delete=models.PROTECT)
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=DOCUMENT_STATUS_CHOICES, default="Pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-order_date", "-created_at"]

    def recalculate_amount(self):
        self.amount = self.items.aggregate(total=models.Sum("total"))["total"] or 0
        self.save(update_fields=["amount"])

    def __str__(self):
        return self.order_number


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.total = line_total(self.quantity, self.unit_price, 0, self.tax_amount)
        super().save(*args, **kwargs)
        self.purchase_order.recalculate_amount()

    def delete(self, *args, **kwargs):
        purchase_order = self.purchase_order
        super().delete(*args, **kwargs)
        purchase_order.recalculate_amount()

    def __str__(self):
        return f"{self.purchase_order} - {self.product}"


class SupplierBill(models.Model):
    bill_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Merchant, on_delete=models.PROTECT)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    bill_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=DOCUMENT_STATUS_CHOICES, default="Pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-bill_date", "-created_at"]

    @property
    def balance_due(self):
        return self.amount - self.paid_amount

    def __str__(self):
        return self.bill_number


class PaymentReceived(models.Model):
    payment_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=50, blank=True)
    reference_no = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]

    def __str__(self):
        return self.payment_number

    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = PaymentReceived.objects.get(pk=self.pk)
        super().save(*args, **kwargs)
        if previous and previous.invoice:
            previous.invoice.paid_amount = PaymentReceived.objects.filter(invoice=previous.invoice).aggregate(total=models.Sum("amount"))["total"] or 0
            previous.invoice.save(update_fields=["paid_amount"])
        if self.invoice:
            self.invoice.paid_amount = PaymentReceived.objects.filter(invoice=self.invoice).aggregate(total=models.Sum("amount"))["total"] or 0
            self.invoice.status = "Inactive" if self.invoice.paid_amount >= self.invoice.amount else "Active"
            self.invoice.save(update_fields=["paid_amount", "status"])

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        if invoice:
            invoice.paid_amount = PaymentReceived.objects.filter(invoice=invoice).aggregate(total=models.Sum("amount"))["total"] or 0
            invoice.status = "Inactive" if invoice.paid_amount >= invoice.amount else "Active"
            invoice.save(update_fields=["paid_amount", "status"])


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
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_rmas")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True)
    closed_date = models.DateField(null=True, blank=True)
    returned_stocked = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-return_date", "-created_at"]

    def __str__(self):
        return self.rma_number


class ReturnHistory(models.Model):
    rma = models.ForeignKey(ReturnRMA, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.rma} - {self.status}"


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


class AppSetting(models.Model):
    company_name = models.CharField(max_length=150, default="SKH Computers")
    currency = models.CharField(max_length=20, default="AED")
    low_stock_threshold = models.PositiveIntegerField(default=5)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    default_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "App Setting"
        verbose_name_plural = "App Settings"

    def __str__(self):
        return self.company_name


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
