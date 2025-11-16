from django.shortcuts import render
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Table, MenuItem, Order, OrderItem, Payment
from .serializers import (TableSerializer, MenuItemSerializer, OrderSerializer, PaymentSerializer,)
# Create your views here.

TAX_RATE = Decimal("0.05")  # 5%


@api_view(["GET"])
def list_tables(request):
    tables = Table.objects.all().order_by("id")
    ser = TableSerializer(tables, many=True)
    return Response(ser.data)


@api_view(["POST"])
def occupy_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    if table.status == "occupied":
        return Response(
            {"error": "Table is already occupied"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    table.status = "occupied"
    table.save()
    return Response({"message": "Table occupied", "table": TableSerializer(table).data})


@api_view(["GET"])
def list_menu(request):
    items = MenuItem.objects.filter(is_available=True).order_by("category", "name")
    data = {}
    for item in items:
        cat = item.category
        if cat not in data:
            data[cat] = []
        data[cat].append(MenuItemSerializer(item).data)
    return Response(data)



@api_view(["POST"])
@transaction.atomic
def create_order(request):
    table_id = request.data.get("table_id")
    items = request.data.get("items", [])

    if not table_id or not items:
        return Response(
            {"error": "table_id and items are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    table = get_object_or_404(Table, id=table_id)

    if table.status == "available":
        table.status = "occupied"
        table.save()

    order = Order.objects.create(table=table, status="active")

    subtotal = Decimal("0.00")

    for item in items:
        menu_id = item.get("menu_id")
        qty = item.get("qty", 1)

        if not menu_id or qty <= 0:
            return Response(
                {"error": "Each item must have menu_id and qty > 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        menu_item = get_object_or_404(MenuItem, id=menu_id)

        if not menu_item.is_available:
            return Response(
                {"error": f"Menu item '{menu_item.name}' is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unit_price = menu_item.price
        line_total = unit_price * qty

        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=qty,
            unit_price=unit_price,
            line_total=line_total,
        )

        subtotal += line_total

    order.subtotal = subtotal
    order.save()

    return Response(
        {"message": "Order created", "order": OrderSerializer(order).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT"])
@transaction.atomic
def add_items_to_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "active":
        return Response(
            {"error": "Cannot add items to a completed order"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    items = request.data.get("items", [])
    if not items:
        return Response(
            {"error": "items list is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    subtotal = order.subtotal

    for item in items:
        menu_id = item.get("menu_id")
        qty = item.get("qty", 1)

        if not menu_id or qty <= 0:
            return Response(
                {"error": "Each item must have menu_id and qty > 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        menu_item = get_object_or_404(MenuItem, id=menu_id)
        if not menu_item.is_available:
            return Response(
                {"error": f"Menu item '{menu_item.name}' is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unit_price = menu_item.price
        line_total = unit_price * qty

        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=qty,
            unit_price=unit_price,
            line_total=line_total,
        )

        subtotal += line_total

    order.subtotal = subtotal
    order.save()

    return Response(
        {"message": "Items added", "order": OrderSerializer(order).data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def get_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    ser = OrderSerializer(order)
    return Response(ser.data)


@api_view(["POST"])
@transaction.atomic
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "active":
        return Response(
            {"error": "Order is already completed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    subtotal = Decimal("0.00")
    for item in order.items.all():
        subtotal += item.line_total

    tax = subtotal * TAX_RATE
    total = subtotal + tax

    order.subtotal = subtotal
    order.tax = tax.quantize(Decimal("0.01"))
    order.total = total.quantize(Decimal("0.01"))
    order.status = "completed"
    order.save()

    return Response(
        {
            "message": "Order completed, bill generated",
            "order": OrderSerializer(order).data,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
def list_active_orders(request):
    orders = Order.objects.filter(status="active").order_by("-created_at")
    ser = OrderSerializer(orders, many=True)
    return Response(ser.data)
    
@api_view(["POST"])
@transaction.atomic
def process_payment(request):
    order_id = request.data.get("order_id")
    amount = request.data.get("amount")
    method = request.data.get("method")

    if not order_id or amount is None or not method:
        return Response(
            {"error": "order_id, amount and method are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order = get_object_or_404(Order, id=order_id)

    if order.status != "completed":
        return Response(
            {"error": "Order must be completed before payment"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if hasattr(order, "payment"):
        return Response(
            {"error": "Payment already processed for this order"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    amount = Decimal(str(amount))
    if amount != order.total:
        return Response(
            {"error": f"Amount {amount} does not match order total {order.total}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment = Payment.objects.create(order=order, amount=amount, method=method)

    table = order.table
    table.status = "available"
    table.save()

    return Response(
        {
            "message": "Payment processed, table released",
            "payment": PaymentSerializer(payment).data,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
def get_active_order_by_table(request, table_id):
    try:
        order = Order.objects.get(table_id=table_id, status="active")
        return Response({"exists": True, "order_id": order.id})
    except Order.DoesNotExist:
        return Response({"exists": False})

