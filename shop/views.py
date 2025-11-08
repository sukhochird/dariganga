from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse
from django.utils.http import urlencode
from .models import Category, Subcategory, Product, ProductImage, LandingPageContent
from .forms import CategoryForm, SubcategoryForm, ProductForm, ProductImageForm, LandingPageContentForm


@login_required
def dashboard(request):
    """Main admin dashboard"""
    context = {
        'total_categories': Category.objects.count(),
        'total_subcategories': Subcategory.objects.count(),
        'total_products': Product.objects.count(),
        'total_landing_contents': LandingPageContent.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'featured_products': Product.objects.filter(is_featured=True).count(),
        'recent_products': Product.objects.all()[:5],
        'low_stock_products': Product.objects.filter(stock_quantity__lt=10).order_by('stock_quantity')[:5],
    }
    return render(request, 'shop/dashboard.html', context)


# Category Views
@login_required
def category_list(request):
    """Manage categories and subcategories from a single page"""
    active_tab = request.GET.get('tab', 'categories')
    category_search = request.GET.get('category_search', '')
    subcategory_search = request.GET.get('subcategory_search', '')
    subcategory_category = request.GET.get('subcategory_category', '')

    categories_qs = Category.objects.all()
    if category_search:
        categories_qs = categories_qs.filter(
            Q(name__icontains=category_search) |
            Q(description__icontains=category_search)
        )
    categories = categories_qs.annotate(
        product_count=Count('products')
    ).order_by('sort_order', 'name')

    subcategories_qs = Subcategory.objects.select_related('category')
    if subcategory_search:
        subcategories_qs = subcategories_qs.filter(
            Q(name__icontains=subcategory_search) |
            Q(description__icontains=subcategory_search)
        )
    if subcategory_category:
        subcategories_qs = subcategories_qs.filter(category_id=subcategory_category)
    subcategories = subcategories_qs.annotate(
        product_count=Count('products')
    ).order_by('sort_order', 'name')

    category_form = CategoryForm()
    subcategory_form = SubcategoryForm()

    if request.method == 'POST':
        category_search = request.POST.get('category_search', category_search)
        subcategory_search = request.POST.get('subcategory_search', subcategory_search)
        subcategory_category = request.POST.get('subcategory_category', subcategory_category)
        active_tab = request.POST.get('tab', active_tab)
        form_type = request.POST.get('form_type')
        redirect_params = {
            'category_search': request.POST.get('category_search', ''),
            'subcategory_search': request.POST.get('subcategory_search', ''),
            'subcategory_category': request.POST.get('subcategory_category', ''),
        }

        if form_type == 'category':
            category_form = CategoryForm(request.POST, request.FILES)
            active_tab = 'categories'
            redirect_params['tab'] = 'categories'

            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Ангилал амжилттай үүслээ!')
                query_string = urlencode({k: v for k, v in redirect_params.items() if v})
                redirect_url = reverse('category_list')
                if query_string:
                    redirect_url = f"{redirect_url}?{query_string}"
                return redirect(f"{redirect_url}#categories")
        elif form_type == 'subcategory':
            subcategory_form = SubcategoryForm(request.POST, request.FILES)
            active_tab = 'subcategories'
            redirect_params['tab'] = 'subcategories'

            if subcategory_form.is_valid():
                subcategory_form.save()
                messages.success(request, 'Дэд ангилал амжилттай үүслээ!')
                query_string = urlencode({k: v for k, v in redirect_params.items() if v})
                redirect_url = reverse('category_list')
                if query_string:
                    redirect_url = f"{redirect_url}?{query_string}"
                return redirect(f"{redirect_url}#subcategories")

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'category_form': category_form,
        'subcategory_form': subcategory_form,
        'category_search': category_search,
        'subcategory_search': subcategory_search,
        'subcategory_category': subcategory_category,
        'active_tab': active_tab,
        'all_categories': Category.objects.order_by('name'),
    }
    return render(request, 'shop/category_list.html', context)


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ангилал амжилттай үүслээ!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'shop/category_form.html', {'form': form, 'action': 'Үүсгэх'})


@login_required
def category_edit(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ангилал амжилттай засагдлаа!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'shop/category_form.html', {'form': form, 'action': 'Засах', 'category': category})


@login_required
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Ангилал амжилттай устгагдлаа!')
        return redirect('category_list')
    
    return render(request, 'shop/category_confirm_delete.html', {'category': category})


# Subcategory Views
@login_required
def subcategory_list(request):
    """Redirect to unified category management page with subcategory tab active"""
    redirect_params = {
        'tab': 'subcategories',
        'subcategory_search': request.GET.get('search', ''),
        'subcategory_category': request.GET.get('category', ''),
        'category_search': request.GET.get('category_search', ''),
    }
    query_string = urlencode({k: v for k, v in redirect_params.items() if v})
    redirect_url = reverse('category_list')
    if query_string:
        redirect_url = f"{redirect_url}?{query_string}"
    return redirect(f"{redirect_url}#subcategories")


@login_required
def subcategory_create(request):
    """Create a new subcategory"""
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дэд ангилал амжилттай үүслээ!')
            return redirect('subcategory_list')
    else:
        form = SubcategoryForm()
    
    return render(request, 'shop/subcategory_form.html', {'form': form, 'action': 'Үүсгэх'})


@login_required
def subcategory_edit(request, pk):
    """Edit an existing subcategory"""
    subcategory = get_object_or_404(Subcategory, pk=pk)
    
    if request.method == 'POST':
        form = SubcategoryForm(request.POST, request.FILES, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дэд ангилал амжилттай засагдлаа!')
            return redirect('subcategory_list')
    else:
        form = SubcategoryForm(instance=subcategory)
    
    return render(request, 'shop/subcategory_form.html', {'form': form, 'action': 'Засах', 'subcategory': subcategory})


@login_required
def subcategory_delete(request, pk):
    """Delete a subcategory"""
    subcategory = get_object_or_404(Subcategory, pk=pk)
    
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, 'Дэд ангилал амжилттай устгагдлаа!')
        return redirect('subcategory_list')
    
    return render(request, 'shop/subcategory_confirm_delete.html', {'subcategory': subcategory})


# Product Views
@login_required
def product_list(request):
    """List all products"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    subcategory_filter = request.GET.get('subcategory', '')
    
    products = Product.objects.select_related('category', 'subcategory').prefetch_related('images')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if subcategory_filter:
        products = products.filter(subcategory_id=subcategory_filter)
    
    products = products.order_by('-created_at')
    
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'subcategories': subcategories,
        'search_query': search_query,
        'category_filter': category_filter,
        'subcategory_filter': subcategory_filter,
    }
    return render(request, 'shop/product_list.html', context)


@login_required
def product_create(request):
    """Create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_main=(i == 0),
                    sort_order=i
                )
            
            messages.success(request, 'Бүтээгдэхүүн амжилттай үүслээ!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'shop/product_form.html', {'form': form, 'action': 'Үүсгэх'})


@login_required
def product_edit(request, pk):
    """Edit an existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            
            # Handle new image uploads
            images = request.FILES.getlist('images')
            if images:
                current_count = product.images.count()
                for i, image in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_main=(current_count == 0 and i == 0),
                        sort_order=current_count + i
                    )
            
            messages.success(request, 'Бүтээгдэхүүн амжилттай засагдлаа!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'action': 'Засах',
        'product': product,
        'images': product.images.all()
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


@login_required
def product_image_delete(request, pk):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, pk=pk)
    product_id = image.product.id
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Зураг амжилттай устгагдлаа!')
        return redirect('product_edit', pk=product_id)
    
    return render(request, 'shop/image_confirm_delete.html', {'image': image})


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
