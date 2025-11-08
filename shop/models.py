from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Category model with name, sort order, and image"""
    name = models.CharField(max_length=200, verbose_name="Нэр")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="Зураг")
    description = models.TextField(blank=True, verbose_name="Тайлбар")
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Засварласан огноо")

    class Meta:
        verbose_name = "Ангилал"
        verbose_name_plural = "Ангиллууд"
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Subcategory model linked to Category"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="Ангилал")
    name = models.CharField(max_length=200, verbose_name="Нэр")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    image = models.ImageField(upload_to='subcategories/', null=True, blank=True, verbose_name="Зураг")
    description = models.TextField(blank=True, verbose_name="Тайлбар")
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Засварласан огноо")

    class Meta:
        verbose_name = "Дэд ангилал"
        verbose_name_plural = "Дэд ангиллууд"
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):
    """Product model with multiple images and specifications"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Ангилал")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Дэд ангилал")
    name = models.CharField(max_length=300, verbose_name="Нэр")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(verbose_name="Танилцуулга")
    specifications = models.TextField(blank=True, help_text="Үзүүлэлтүүдийг мөр мөрөөр нь оруулна уу", verbose_name="Үзүүлэлтүүд")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Үнэ")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Хямдралтай үнэ")
    stock_quantity = models.IntegerField(default=0, verbose_name="Нөөц")
    is_featured = models.BooleanField(default=False, verbose_name="Онцлох бүтээгдэхүүн")
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй")
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Засварласан огноо")

    class Meta:
        verbose_name = "Бүтээгдэхүүн"
        verbose_name_plural = "Бүтээгдэхүүнүүд"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def main_image(self):
        """Get the first image as main image"""
        return self.images.filter(is_main=True).first() or self.images.first()

    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price


class ProductImage(models.Model):
    """Multiple images for a product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Бүтээгдэхүүн")
    image = models.ImageField(upload_to='products/', verbose_name="Зураг")
    is_main = models.BooleanField(default=False, verbose_name="Үндсэн зураг")
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")

    class Meta:
        verbose_name = "Бүтээгдэхүүний зураг"
        verbose_name_plural = "Бүтээгдэхүүний зургууд"
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # If this is set as main image, unset others
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class LandingPageContent(models.Model):
    """Landing page content sections"""
    SECTION_TYPES = [
        ('hero', 'Hero Section'),
        ('features', 'Features Section'),
        ('about', 'About Section'),
        ('testimonials', 'Testimonials'),
        ('cta', 'Call to Action'),
        ('custom', 'Custom Section'),
    ]

    title = models.CharField(max_length=300, verbose_name="Гарчиг")
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES, default='custom', verbose_name="Хэсгийн төрөл")
    subtitle = models.CharField(max_length=500, blank=True, verbose_name="Дэд гарчиг")
    content = models.TextField(blank=True, verbose_name="Агуулга")
    image = models.ImageField(upload_to='landing/', null=True, blank=True, verbose_name="Зураг")
    button_text = models.CharField(max_length=100, blank=True, verbose_name="Товчны текст")
    button_link = models.CharField(max_length=500, blank=True, verbose_name="Товчны холбоос")
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Засварласан огноо")

    class Meta:
        verbose_name = "Landing хуудасны агуулга"
        verbose_name_plural = "Landing хуудасны агуулгууд"
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title}"
