from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_reintroduce_subcategories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/gallery/', verbose_name='Зураг')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Эрэмбэ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Үүсгэсэн огноо')),
                ('product', models.ForeignKey(on_delete=models.CASCADE, related_name='images', to='shop.product', verbose_name='Бүтээгдэхүүн')),
            ],
            options={
                'verbose_name': 'Бүтээгдэхүүний зураг',
                'verbose_name_plural': 'Бүтээгдэхүүний зургууд',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]

