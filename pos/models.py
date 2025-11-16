from django.db import models
from django.utils import timezone
from decimal import Decimal
# Create your models here.

class Table(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("occupied", "Occupied"),
    )
    name = models.CharField(max_length=50, unique=True) 
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="available"
    )

    def __str__(self):
        return f"{self.name} ({self.status})"


class MenuItem(models.Model):
    CATEGORY_CHOICES = (
        ("food", "Food"),
        ("drink", "Drink"),
        ("dessert", "Dessert"),
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
    )
    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"Order {self.id} - Table {self.table.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity} (Order {self.order.id})"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("cash", "Cash"),
        ("card", "Card"),
    )
    order = models.OneToOneField(
        Order, on_delete=models.PROTECT, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    paid_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.amount} ({self.method})"
