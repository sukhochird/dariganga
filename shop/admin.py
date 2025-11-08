from django.contrib import admin
from .models import Category, Product, Banner, LandingPageContent, SubCategory, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'sort_order']
    list_filter = []
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'sort_order']
    list_filter = ['category']
    search_fields = ['name', 'slug', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category__name', 'sort_order', 'name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'sort_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'slug', 'created_at']
    list_filter = ['category', 'subcategory', 'created_at']
    search_fields = ['name', 'description', 'slug', 'subcategory__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['-created_at']
    inlines = [ProductImageInline]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'created_at']
    list_editable = ['order']
    ordering = ['order', 'id']


@admin.register(LandingPageContent)
class LandingPageContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'section_type', 'sort_order', 'is_active', 'created_at']
    list_filter = ['section_type', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['sort_order']
