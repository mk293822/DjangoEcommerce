from django.contrib import admin
from guardian.shortcuts import get_objects_for_user
import nested_admin

class ObjectPermissionMixin:
    def has_change_permission(self, request, obj=None):

        if request.user.is_superuser or obj is None:
            return True

        return request.user.has_perm(f"{self.opts.app_label}.change_{self.opts.model_name}", obj)


    def has_delete_permission(self, request, obj=None):

        if request.user.is_superuser or obj is None:
            return True

        return request.user.has_perm(f"{self.opts.app_label}.delete_{self.opts.model_name}", obj)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        filter_by = None
        
        if hasattr(qs.model, 'created_by'):
            filter_by = 'created_by'
        elif hasattr(qs.model, 'product'):
            filter_by = 'product__created_by'
        elif hasattr(qs.model, 'variation_typ'):
            filter_by = 'variation_type__product__created_by'
        elif hasattr(qs.model, 'variation_type_option'):
            filter_by = 'variation_type_option__variation_type__product__created_by'
        
        if filter_by:
            qs  = qs.filter(**{filter_by: request.user})
        
        return get_objects_for_user(request.user, f"products.view_{self.opts.model_name}", qs)

class ModelAdmin(ObjectPermissionMixin, admin.ModelAdmin):
    pass
      
class NestedAdmin(ObjectPermissionMixin, nested_admin.NestedModelAdmin):
    pass

class NestedAdminInline(ObjectPermissionMixin, nested_admin.NestedTabularInline):
    pass

