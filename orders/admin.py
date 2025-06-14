from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInlineAdmin(admin.StackedInline):
    model = OrderItem
    readonly_fields = ('created_at', 'updated_at')
    min_num = 1
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'created_at', 'updated_at')
    list_filter = ('status', )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInlineAdmin]
