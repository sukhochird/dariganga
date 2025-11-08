from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Max
from django.forms import inlineformset_factory
from rest_framework import viewsets

from .models import Category, Product, Banner, LandingPageContent, SubCategory, ProductImage
from .forms import CategoryForm, SubCategoryForm, ProductForm, LandingPageContentForm, BannerForm
from .serializers import CategorySerializer, ProductSerializer, BannerSerializer


@login_required
def dashboard(request):
    """Main admin dashboard"""
    top_level_categories = Category.objects.all().order_by('sort_order', 'name')

    context = {
        'total_categories': top_level_categories.count(),
        'total_subcategories': SubCategory.objects.count(),
        'total_products': Product.objects.count(),
        'total_banners': Banner.objects.count(),
        'total_landing_contents': LandingPageContent.objects.count(),
        'recent_products': Product.objects.select_related('category', 'subcategory').order_by('-created_at')[:5],
        'top_categories': top_level_categories.annotate(
            product_total=Count('products'),
            subcategory_count=Count('subcategories')
        ).order_by('-product_total', 'name')[:5],
    }
    return render(request, 'shop/dashboard.html', context)


# Category Views
@login_required
def category_list(request):
    """Manage categories and subcategories from a single page"""
    category_search = request.GET.get('category_search', '')

    categories = Category.objects.all()
    if category_search:
        categories = categories.filter(name__icontains=category_search)
    categories = categories.annotate(subcategory_count=Count('subcategories')).prefetch_related('subcategories').order_by('sort_order', 'name')

    context = {
        'categories': categories,
        'category_search': category_search,
    }
    return render(request, 'shop/category_list.html', context)


SubCategoryFormSet = inlineformset_factory(
    Category,
    SubCategory,
    form=SubCategoryForm,
    extra=1,
    can_delete=True,
)


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        dummy_instance = Category()
        formset = SubCategoryFormSet(request.POST, request.FILES, instance=dummy_instance, prefix='subcategories')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                category = form.save()
                formset.instance = category
                formset.save()
            messages.success(request, 'Ангилал амжилттай үүслээ!')
            return redirect('category_list')
    else:
        form = CategoryForm()
        formset = SubCategoryFormSet(instance=Category(), prefix='subcategories')

    return render(
        request,
        'shop/category_form.html',
        {
            'form': form,
            'formset': formset,
            'action': 'Үүсгэх',
        },
    )


@login_required
def category_edit(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        formset = SubCategoryFormSet(request.POST, request.FILES, instance=category, prefix='subcategories')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Ангилал амжилттай засагдлаа!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
        formset = SubCategoryFormSet(instance=category, prefix='subcategories')

    return render(
        request,
        'shop/category_form.html',
        {
            'form': form,
            'formset': formset,
            'action': 'Засах',
            'category': category,
        },
    )


@login_required
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Ангилал амжилттай устгагдлаа!')
        return redirect('category_list')

    return render(request, 'shop/category_confirm_delete.html', {'category': category})


# Product Views
@login_required
def product_list(request):
    """List all products"""
    search_query = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')
    subcategory_slug = request.GET.get('subcategory', '')

    products = Product.objects.select_related('category', 'subcategory').prefetch_related('images')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)

    products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': Category.objects.all().order_by('sort_order', 'name'),
        'subcategories': SubCategory.objects.select_related('category').order_by('category__name', 'name'),
        'search_query': search_query,
        'category_filter': category_slug,
        'subcategory_filter': subcategory_slug,
    }
    return render(request, 'shop/product_list.html', context)


@login_required
def product_create(request):
    """Create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            new_images = request.FILES.getlist('additional_images')
            if new_images:
                max_order = product.images.aggregate(max_order=Max('sort_order'))['max_order']
                next_order = (max_order + 1) if max_order is not None else 0
                for offset, image_file in enumerate(new_images):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        sort_order=next_order + offset,
                    )
            messages.success(request, 'Бүтээгдэхүүн амжилттай үүслээ!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(
        request,
        'shop/product_form.html',
        {
            'form': form,
            'action': 'Үүсгэх',
            'product': None,
            'gallery': [],
        },
    )


@login_required
def product_edit(request, pk):
    """Edit an existing product"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                ProductImage.objects.filter(product=product, id__in=delete_ids).delete()

            new_images = request.FILES.getlist('additional_images')
            if new_images:
                max_order = product.images.aggregate(max_order=Max('sort_order'))['max_order']
                next_order = (max_order + 1) if max_order is not None else 0
                for offset, image_file in enumerate(new_images):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        sort_order=next_order + offset,
                    )
            messages.success(request, 'Бүтээгдэхүүн амжилттай засагдлаа!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'action': 'Засах',
        'product': product,
        'gallery': product.images.all(),
    }
    return render(request, 'shop/product_form.html', context)


@login_required
def product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Бүтээгдэхүүн амжилттай устгагдлаа!')
        return redirect('product_list')

    return render(request, 'shop/product_confirm_delete.html', {'product': product})


# Landing Page Content Views
@login_required
def landing_content_list(request):
    """List all landing page contents"""
    search_query = request.GET.get('search', '')
    section_filter = request.GET.get('section', '')

    contents = LandingPageContent.objects.all()

    if search_query:
        contents = contents.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    if section_filter:
        contents = contents.filter(section_type=section_filter)

    contents = contents.order_by('sort_order')

    context = {
        'contents': contents,
        'search_query': search_query,
        'section_filter': section_filter,
        'section_types': LandingPageContent.SECTION_TYPES,
    }
    return render(request, 'shop/landing_content_list.html', context)


@login_required
def landing_content_create(request):
    """Create a new landing page content"""
    if request.method == 'POST':
        form = LandingPageContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Landing хуудасны агуулга амжилттай үүслээ!')
            return redirect('landing_content_list')
    else:
        form = LandingPageContentForm()

    return render(request, 'shop/landing_content_form.html', {'form': form, 'action': 'Үүсгэх'})


@login_required
def landing_content_edit(request, pk):
    """Edit an existing landing page content"""
    content = get_object_or_404(LandingPageContent, pk=pk)

    if request.method == 'POST':
        form = LandingPageContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Landing хуудасны агуулга амжилттай засагдлаа!')
            return redirect('landing_content_list')
    else:
        form = LandingPageContentForm(instance=content)

    return render(request, 'shop/landing_content_form.html', {'form': form, 'action': 'Засах', 'content': content})


@login_required
def landing_content_delete(request, pk):
    """Delete a landing page content"""
    content = get_object_or_404(LandingPageContent, pk=pk)

    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Landing хуудасны агуулга амжилттай устгагдлаа!')
        return redirect('landing_content_list')

    return render(request, 'shop/landing_content_confirm_delete.html', {'content': content})


# API ViewSets
class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.all().order_by('order', 'id')
    serializer_class = BannerSerializer


# Banner Views
@login_required
def banner_list(request):
    banners = Banner.objects.all().order_by('order', 'id')
    return render(request, 'shop/banner_list.html', {'banners': banners})


@login_required
def banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Баннер амжилттай үүслээ!')
            return redirect('banner_list')
    else:
        form = BannerForm()
    return render(request, 'shop/banner_form.html', {'form': form, 'action': 'Үүсгэх'})


@login_required
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Баннер амжилттай засагдлаа!')
            return redirect('banner_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'shop/banner_form.html', {'form': form, 'action': 'Засах', 'banner': banner})


@login_required
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Баннер амжилттай устгагдлаа!')
        return redirect('banner_list')
    return render(request, 'shop/banner_confirm_delete.html', {'banner': banner})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all().order_by('sort_order', 'name').prefetch_related('subcategories')


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images').order_by('-created_at')
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
