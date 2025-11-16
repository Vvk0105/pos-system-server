from rest_framework import serializers
from .models import Table, MenuItem, Order, OrderItem, Payment


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["id", "name", "status"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "price", "category", "is_available"]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "menu_item_name", "quantity", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_name = serializers.CharField(source="table.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "table",
            "table_name",
            "status",
            "created_at",
            "updated_at",
            "subtotal",
            "tax",
            "total",
            "items",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "order_id", "amount", "method", "paid_at"]
