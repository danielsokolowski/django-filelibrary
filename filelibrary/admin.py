""" Various default admin over ries """
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect, get_object_or_404
from filelibrary.models import FileCategory, File
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_groups_with_perms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse


class FileCategoryAdmin(admin.ModelAdmin):
    ### list_display callables
    def site_url(obj):
        try:
            return "<a href='%s'>%s</a>" % (obj.get_absolute_url(), obj.get_absolute_url())
        except AttributeError:
            return "N/A"
    site_url.allow_tags = True

    list_display = ['id', site_url, 'template', 'parent_category', 'name', 'status']
    list_display_links = ['id'] # other columns from list_display to turn into edit link
    list_filter = ['status', 'parent_category', 'template']
    list_editable = ['status']
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name', 'description']
    #ordering = ['parent_category__id', 'order'] #FIXME need to update to django 1.4
    save_on_top = True

admin.site.register(FileCategory , FileCategoryAdmin)

class FileAdmin(GuardedModelAdmin, admin.ModelAdmin):
    ### list_display callables
    def site_url(obj):
        try:
            return "<a href='%s'>%s</a>" % (obj.get_absolute_url(), obj.get_absolute_url())
        except AttributeError:
            return "N/A"
    site_url.allow_tags = True

    ### additional admin actions for this model
    def auth_groups(obj): #, request, queryset):
        model_groups = Group.objects.filter(permissions__content_type=ContentType.objects.get_for_model(obj)).distinct()
        instance_groups = get_groups_with_perms(obj) # distinct() has already been applied to result
        output_html = 'Group Level: '
        from django.utils.functional import lazy # stupid eager python
        reverse_lazy = lambda name = None, *args : lazy(reverse, str)(name, args=args) # stupid eager python
        for group in model_groups:
            output_html = output_html + '<a href="%s">%s</a>, ' % (reverse_lazy('admin:auth_group_change', group.pk), group.name)
        if instance_groups:
            output_html = output_html[:-2] + '<br>Instance Level: '
            for group in instance_groups:
                output_html = output_html + '<a href="%s/permissions/">%s</a>, ' % (obj.pk, group.name)
        return output_html[:-2]
    auth_groups.allow_tags = True

    list_display = ['id', 'status', site_url, auth_groups, 'category', 'name']
    list_display_links = ['id'] # other columns from list_display to turn into edit link
    list_filter = ['category', 'status']
    search_fields = ['name', 'description']
    #ordering = ['parent_category__id', 'order'] #FIXME need to update to django 1.4
    save_on_top = True
admin.site.register(File, FileAdmin)
