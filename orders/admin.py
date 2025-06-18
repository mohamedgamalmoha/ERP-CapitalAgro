from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from orders.models import Order, OrderItem
from orders.views import SupplyChainHierarchyAdminView


class OrderItemInlineAdmin(admin.StackedInline):
    model = OrderItem
    readonly_fields = ('created_at', 'updated_at')
    min_num = 1
    extra = 1


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'created_at', 'updated_at')
    readonly_fields = ('supply_chain_hierarchy', 'created_at', 'updated_at')

    def get_urls(self):
        return [
            path(
                "<str:id>/supply_chain_hierarchy/",
                SupplyChainHierarchyAdminView.as_view(model_admin=self),
                name=f"supply_chain_hierarchy",
            ),
            * super().get_urls(),
        ]

    def supply_chain_hierarchy(self, obj):
        url = reverse("admin:supply_chain_hierarchy", args=[obj.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            _("View Supply Chain Hierarchy")
        )

    supply_chain_hierarchy.short_description = _("Supply Chain Hierarchy")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'created_at', 'updated_at')
    list_filter = ('status', )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInlineAdmin]
