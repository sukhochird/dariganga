from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Subcategory URLs
    path('subcategories/', views.subcategory_list, name='subcategory_list'),
    path('subcategories/create/', views.subcategory_create, name='subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategories/<int:pk>/delete/', views.subcategory_delete, name='subcategory_delete'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product-images/<int:pk>/delete/', views.product_image_delete, name='product_image_delete'),
    
    # Landing Page Content URLs
    path('landing-contents/', views.landing_content_list, name='landing_content_list'),
    path('landing-contents/create/', views.landing_content_create, name='landing_content_create'),
    path('landing-contents/<int:pk>/edit/', views.landing_content_edit, name='landing_content_edit'),
    path('landing-contents/<int:pk>/delete/', views.landing_content_delete, name='landing_content_delete'),
]

