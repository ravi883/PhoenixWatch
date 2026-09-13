from django.urls import path

from . import views


app_name = "cart"


urlpatterns = [

    path("", views.cart_view, name="cart-view"),
    path("add/<product_id>/",views.add_to_cart,name="add_to_cart"),
    path("update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("remove/<int:item_id>/",  views.remove_cart_item,name="remove_cart_item"),
    path( "clear/", views.clear_cart, name="clear_cart"),
    path("count/",views.cart_count,name="cart_count"),
    path("drawer/",views.cart_drawer_view,name="cart-drawer"),
]