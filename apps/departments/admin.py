from django.contrib import admin
from .models import Department, Category

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'meta_title', 'numbers_of_categories')
    exclude = ('slug',)
    inlines = [CategoryInline]
    search_fields = ('name', 'slug')
    sortable_by = ('name', 'slug', 'status', 'numbers_of_categories')

    def numbers_of_categories(self, obj):
        return obj.categories.count()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name', 'department')
    sortable_by = ('department', 'name')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = ...):
        return False
    
    def has_delete_permission(self, request, obj = ...):
        return False
    