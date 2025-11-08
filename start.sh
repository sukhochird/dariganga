#!/bin/bash

echo "🚀 E-Commerce Admin системийг эхлүүлж байна..."
echo ""

# Activate virtual environment
source env/bin/activate

# Check if superuser exists
echo "📝 Superuser шалгаж байна..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('✅ Superuser байна' if User.objects.filter(is_superuser=True).exists() else '❌ Superuser байхгүй байна')"

echo ""
echo "🌐 Сервер асааж байна..."
echo ""
echo "Дараах хаягаар нэвтэрнэ үү:"
echo "👉 http://127.0.0.1:8000/"
echo ""
echo "Django Admin панел:"
echo "👉 http://127.0.0.1:8000/admin/"
echo ""
echo "Серверийг зогсоохын тулд Ctrl+C дарна уу"
echo ""

python manage.py runserver

