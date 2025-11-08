from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Top-level product category."""

    name = models.CharField(max_length=200, verbose_name="Нэр")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Зураг")

    class Meta:
        verbose_name = "Ангилал"
        verbose_name_plural = "Ангиллууд"
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            counter = 1
            while Category.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """Second-level category within a category."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="Ангилал",
    )
    name = models.CharField(max_length=200, verbose_name="Нэр")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sort_order = models.IntegerField(default=0, verbose_name="Эрэмбэ")

    class Meta:
        verbose_name = "Дэд ангилал"
        verbose_name_plural = "Дэд ангиллууд"
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            counter = 1
            while SubCategory.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Product(models.Model):
    """Product linked to a single category with optional gallery URLs."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Ангилал",
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name="Дэд ангилал",
        null=True,
        blank=True,
    )
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    name = models.CharField(max_length=300, verbose_name="Нэр")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Үндсэн зураг")
    description = models.TextField(blank=True, verbose_name="Тайлбар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Засварласан огноо")

    class Meta:
        verbose_name = "Бүтээгдэхүүн"
        verbose_name_plural = "Бүтээгдэхүүнүүд"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.subcategory and self.category_id != self.subcategory.category_id:
            self.category = self.subcategory.category
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            counter = 1
            while Product.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Additional product gallery images."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Бүтээгдэхүүн",
    )
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Зураг")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Эрэмбэ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")

    class Meta:
        verbose_name = "Бүтээгдэхүүний зураг"
        verbose_name_plural = "Бүтээгдэхүүний зургууд"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} зураг #{self.pk}"


class Banner(models.Model):
    """Homepage banners displayed in a specific order."""

    image = models.ImageField(upload_to='banners/', verbose_name="Зураг")
    order = models.IntegerField(default=0, verbose_name="Эрэмбэ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Засварласан огноо")

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннерууд"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Banner #{self.pk}"


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
