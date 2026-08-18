from django.db import models


STATUS_CHOICES = [
    ("Active", "Active"),
    ("Inactive", "Inactive"),
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
