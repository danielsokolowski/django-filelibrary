from filelibrary.models import FileCategory
def primary_file_categories(request):
    """
    Add filecategory to all templates
    """
    return {'primary_file_categories': FileCategory.objects.active().filter(parent_category__isnull = True)}