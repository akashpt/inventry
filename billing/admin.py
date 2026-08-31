from django.contrib import admin

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


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "location", "manager_name", "status")
    search_fields = ("code", "name", "location")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("movement_date", "movement_type", "product", "quantity", "from_warehouse", "to_warehouse", "status")
    list_filter = ("movement_type", "status")
    search_fields = ("product__name", "reference_no", "barcode")


@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "product", "quantity", "updated_at")
    list_filter = ("warehouse",)
    search_fields = ("warehouse__name", "warehouse__code", "product__name", "product__sku")


@admin.register(RefurbishmentJob)
class RefurbishmentJobAdmin(admin.ModelAdmin):
    list_display = ("intake_no", "model_name", "serial_no", "qc_technician", "production_status", "supplier_status")
    list_filter = ("production_status",)
    search_fields = ("intake_no", "model_name", "serial_no")


@admin.register(ProductionTask)
class ProductionTaskAdmin(admin.ModelAdmin):
    list_display = ("job", "task_date", "stage", "assigned_to", "status")
    list_filter = ("stage", "status")
    search_fields = ("job__intake_no", "assigned_to", "issue_found")


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quotation_number", "customer", "quotation_date", "valid_until", "amount", "status")
    list_filter = ("status",)
    search_fields = ("quotation_number", "customer__display_name")


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "order_date", "expected_delivery_date", "amount", "status")
    list_filter = ("status",)
    search_fields = ("order_number", "customer__display_name")


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ("delivery_number", "sales_order", "customer", "delivery_date", "tracking_no", "status")
    list_filter = ("status",)
    search_fields = ("delivery_number", "tracking_no", "customer__display_name")


@admin.register(ReturnRMA)
class ReturnRMAAdmin(admin.ModelAdmin):
    list_display = ("rma_number", "customer", "product", "return_date", "approval_status", "resolution")
    list_filter = ("approval_status",)
    search_fields = ("rma_number", "customer__display_name", "product__name")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "status")
    list_filter = ("role", "status")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("activity_date", "user", "module", "action", "object_name")
    list_filter = ("module", "action")
    search_fields = ("module", "action", "object_name")
