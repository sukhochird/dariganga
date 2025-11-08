from django import forms

from .models import Category, Product, LandingPageContent, SubCategory, Banner

BASE_INPUT_CLASS = 'mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
TEXTAREA_INPUT_CLASS = 'mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-3 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
FILE_INPUT_CLASS = 'mt-1 block w-full text-base text-gray-600 file:mr-4 file:py-2.5 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if data in self.empty_values:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []
        errors = []
        for uploaded_file in data:
            try:
                cleaned_files.append(super().clean(uploaded_file, initial))
            except forms.ValidationError as exc:
                errors.extend(exc.error_list)

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_files


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'sort_order', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Ангиллын нэр'
            }),
            'slug': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'slug-хэлбэр (жишээ нь: electronics)',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Эрэмбэ (жишээ нь 0)'
            }),
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS,
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'Slug-ийг гараар оруулж болно. Хоосон үлдээвэл автоматаар тооцоологдоно.'


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Дэд ангиллын нэр'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASS
            }),
        }


class ProductForm(forms.ModelForm):
    additional_images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': FILE_INPUT_CLASS,
            'multiple': True,
        }),
        help_text='Олон зураг сонгох боломжтой.',
    )

    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'name', 'slug', 'image', 'description']
        widgets = {
            'category': forms.Select(attrs={
                'class': BASE_INPUT_CLASS
            }),
            'subcategory': forms.Select(attrs={
                'class': BASE_INPUT_CLASS
            }),
            'name': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Бүтээгдэхүүний нэр'
            }),
            'slug': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'slug-хэлбэр (жишээ нь: leather-bag)',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_INPUT_CLASS,
                'rows': 5,
                'placeholder': 'Тайлбар'
            }),
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS,
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('sort_order', 'name')
        self.fields['subcategory'].required = False
        self.fields['slug'].required = False

        queryset = SubCategory.objects.select_related('category').order_by('category__name', 'name')
        category_id = None
        subcategory_id = None

        if self.data.get('subcategory'):
            try:
                subcategory_id = int(self.data.get('subcategory'))
            except (TypeError, ValueError):
                subcategory_id = None
        elif self.instance and self.instance.pk and self.instance.subcategory_id:
            subcategory_id = self.instance.subcategory_id

        if subcategory_id:
            try:
                subcategory = SubCategory.objects.select_related('category').get(pk=subcategory_id)
                category_id = subcategory.category_id
                queryset = queryset.filter(category_id=category_id)
            except SubCategory.DoesNotExist:
                subcategory = None
        if category_id is None:
            if self.data.get('category'):
                try:
                    category_id = int(self.data.get('category'))
                except (TypeError, ValueError):
                    category_id = None
            elif self.instance and self.instance.pk:
                category_id = self.instance.category_id

        if category_id:
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('sort_order', 'name')
        else:
            self.fields['subcategory'].queryset = queryset.order_by('category__name', 'sort_order', 'name')

    def clean(self):
        cleaned_data = super().clean()
        subcategory = cleaned_data.get('subcategory')
        if subcategory:
            cleaned_data['category'] = subcategory.category
        return cleaned_data


class LandingPageContentForm(forms.ModelForm):
    class Meta:
        model = LandingPageContent
        fields = ['title', 'section_type', 'subtitle', 'content', 'image',
                  'button_text', 'button_link', 'sort_order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Гарчиг'
            }),
            'section_type': forms.Select(attrs={
                'class': BASE_INPUT_CLASS
            }),
            'subtitle': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Дэд гарчиг'
            }),
            'content': forms.Textarea(attrs={
                'class': TEXTAREA_INPUT_CLASS,
                'rows': 5,
                'placeholder': 'Агуулга'
            }),
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS,
            }),
            'button_text': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Дэлгэрэнгүй'
            }),
            'button_link': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': '/products/'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': '0'
            }),
        }


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['image', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS,
                'accept': 'image/*',
            }),
            'order': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASS,
                'placeholder': 'Эрэмбэ (жишээ нь 0)',
            }),
        }