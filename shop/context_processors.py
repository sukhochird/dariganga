from django.urls import reverse


def sidebar_navigation(request):
    """Provide sidebar navigation items with active state based on current view."""
    current_name = ''
    if getattr(request, 'resolver_match', None):
        current_name = request.resolver_match.url_name or ''

    menu_items = [
        {
            'id': 'dashboard',
            'label': 'Dashboard',
            'url': reverse('dashboard'),
            'icon_path': "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
            'match_names': {'dashboard'},
        },
        {
            'id': 'categories',
            'label': 'Ангилал',
            'url': reverse('category_list'),
            'icon_path': "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z",
            'match_names': {'category_list', 'category_create', 'category_edit', 'category_delete'},
        },
        {
            'id': 'products',
            'label': 'Бүтээгдэхүүнүүд',
            'url': reverse('product_list'),
            'icon_path': "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
            'match_names': {'product_list', 'product_create', 'product_edit', 'product_delete'},
        },
        {
            'id': 'landing',
            'label': 'Landing агуулга',
            'url': reverse('landing_content_list'),
            'icon_path': "M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z",
            'match_names': {
                'landing_content_list',
                'landing_content_create',
                'landing_content_edit',
                'landing_content_delete',
            },
        },
        {
            'id': 'banners',
            'label': 'Баннер',
            'url': reverse('banner_list'),
            'icon_path': "M4 4h16v12H4zM4 16l8 4 8-4",
            'match_names': {
                'banner_list',
                'banner_create',
                'banner_edit',
                'banner_delete',
            },
        },
    ]

    for item in menu_items:
        item['is_active'] = current_name in item['match_names']

    return {'sidebar_menu': menu_items}

