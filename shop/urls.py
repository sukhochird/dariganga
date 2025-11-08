from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('banners', views.BannerViewSet, basename='banner')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('products', views.ProductViewSet, basename='product')

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Landing Page Content URLs
    path('landing-contents/', views.landing_content_list, name='landing_content_list'),
    path('landing-contents/create/', views.landing_content_create, name='landing_content_create'),
    path('landing-contents/<int:pk>/edit/', views.landing_content_edit, name='landing_content_edit'),
    path('landing-contents/<int:pk>/delete/', views.landing_content_delete, name='landing_content_delete'),

    # Banner URLs
    path('banners/', views.banner_list, name='banner_list'),
    path('banners/create/', views.banner_create, name='banner_create'),
    path('banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),

    # API
    path('api/', include(router.urls)),
]

