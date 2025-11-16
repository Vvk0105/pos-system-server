from django.urls import path
from . import views

urlpatterns = [
    # Tables
    path("tables/", views.list_tables),
    path("tables/<int:table_id>/occupy/", views.occupy_table),

    # Menu
    path("menu/", views.list_menu),

    # Orders
    path("orders/", views.create_order),
    path("orders/active/", views.list_active_orders),
    path("orders/<int:order_id>/", views.get_order),
    path("orders/<int:order_id>/add-items/", views.add_items_to_order),
    path("orders/<int:order_id>/complete/", views.complete_order),

    # Payments
    path("payments/", views.process_payment),

]
