from django.contrib import admin
from .models import Department, Category, Product, ProductVariationTypeOptionImage
import nested_admin

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'meta_title', 'meta_description', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryInline]
    search_fields = ('name', 'slug')

class ProductVariationTypeOptionImageInline(nested_admin.NestedTabularInline):
    model = ProductVariationTypeOptionImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'department', 'category', 'price', 'stock', 'status', 'image', 'created_at', 'updated_at', )
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('department', 'category')
    
