from django.urls import path
from . import views

urlpatterns = [
    # Authentication related urls
    path('login/', views.login_view, name="login_view"),
    path('register/', views.register_view, name="register_view"),
    path('logout/', views.logout_view, name="logout_view"),

    # Home and Dashboard
    path('', views.home_view, name="home_view"),
    path('products/', views.product_list_view, name="product_list_view"),
    path('farmer/dashboard/', views.farmer_dashboard_view, name="farmer_dashboard_view"),
    path('farmer/product/edit/<int:product_id>/', views.edit_product_view, name="edit_product_view"),
    path('buyer/dashboard/', views.buyer_dashboard_view, name="buyer_dashboard_view"),
]
