from django.db import migrations, models
from django.utils.text import slugify


def migrate_subcategories(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    SubCategory = apps.get_model('shop', 'SubCategory')
    Product = apps.get_model('shop', 'Product')

    db_alias = schema_editor.connection.alias

    child_categories = Category.objects.using(db_alias).filter(parent__isnull=False)
    if not child_categories.exists():
        return

    slug_cache = set(SubCategory.objects.using(db_alias).values_list('slug', flat=True))
    category_to_sub = {}

    for child in child_categories:
        base_slug = child.slug or slugify(child.name) or f"subcategory-{child.pk}"
        slug_candidate = base_slug
        counter = 1

        while slug_candidate in slug_cache:
            slug_candidate = f"{base_slug}-{counter}"
            counter += 1

        subcategory = SubCategory.objects.using(db_alias).create(
            category=child.parent,
            name=child.name,
            slug=slug_candidate,
            sort_order=getattr(child, 'sort_order', 0) or 0,
        )
        slug_cache.add(slug_candidate)
        category_to_sub[child.pk] = subcategory.pk

    products = Product.objects.using(db_alias).filter(category_id__in=category_to_sub.keys())
    for product in products:
        sub_pk = category_to_sub[product.category_id]
        subcategory = SubCategory.objects.using(db_alias).get(pk=sub_pk)
        product.category_id = subcategory.category_id
        product.subcategory_id = sub_pk
        product.save(update_fields=['category', 'subcategory'])

    child_categories.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_catalog_refactor'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='categories/', verbose_name='Зураг'),
        ),
        migrations.AddField(
            model_name='category',
            name='sort_order',
            field=models.IntegerField(default=0, verbose_name='Эрэмбэ'),
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Нэр')),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('sort_order', models.IntegerField(default=0, verbose_name='Эрэмбэ')),
                ('category', models.ForeignKey(on_delete=models.CASCADE, related_name='subcategories', to='shop.category', verbose_name='Ангилал')),
            ],
            options={
                'verbose_name': 'Дэд ангилал',
                'verbose_name_plural': 'Дэд ангиллууд',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='products', to='shop.subcategory', verbose_name='Дэд ангилал'),
        ),
        migrations.RunPython(migrate_subcategories, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='category',
            name='parent',
        ),
    ]

