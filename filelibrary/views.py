from miscellaneous.base_views import MultiFormatResponseMixin
from django.views.generic import ListView, DetailView, FormView, View
from django.views.generic.edit import  FormMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin, SingleObjectMixin
from django.http import Http404, HttpResponse
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from filelibrary.models import FileCategory, File
from filelibrary.forms import FileCategorySearchForm
from django.db.models import Q
from guardian.mixins import PermissionRequiredMixin
import mimetypes
import os


class FileCategoryIndexView(ListView):
    """
    Parent categories only
    """

    #queryset = Ad.objects.none() # default query is empty
    context_object_name = "filecategories"

    def get_queryset(self):
        return FileCategory.objects.current().filter(parent_category__isnull=True) # this is parent category


class FileCategoryDetailView(SingleObjectTemplateResponseMixin, SingleObjectMixin, FormMixin, View):
    """
    Returns a list of categories either in HTML, HTML snippet or (G)JSON fomat - following http GET options are available:
    """

    #queryset = Ad.objects.none() # default query is empty
    context_object_name = "filecategory"
    form_name = 'file_search_form' #non standard variable
    queryset = FileCategory.objects.live()
    form_class = FileCategorySearchForm
    initial = {}
    def get_template_names(self):
        ### go through the auto generated list and generated a specific template to our instance
        names = super(FileCategoryDetailView, self).get_template_names()
        new_names = []
        for name in names:
            new_names.append(name[:-5] + '_' + self.object.template + name[-5:])
        return new_names

    def get_initial(self):
        """ to keep the nomenclature intiuitve we define this function 
        and this synanmous with FormMixin.get_initial() """
        return self.get_form_initial()

    def get_form_initial(self):
        """ returns the initial values for the form """
        return {'search_text': self.request.GET.get('search_text', '')}

    def get_object(self, queryset=None):
        arr_slug_path = self.kwargs['slug_path'].split('/')

        try: # if DoesNotExist throw 404
            if len(arr_slug_path) > 1: # # there is a parent category
                # our categories are unique based on parent_category__slug and category_slug so we only need to search for those
                obj_slug = arr_slug_path.pop()     # get the final slug
                parent_slug = arr_slug_path.pop()   # get the parent slug
                return self.queryset.filter(parent_category__slug=parent_slug).get(slug=obj_slug)
            else:
                obj_slug = arr_slug_path.pop()
                query = self.queryset.filter(parent_category__isnull=True).get(slug=obj_slug) # this is parent category
        except FileCategory.DoesNotExist:
            raise Http404

        return query

    def get_context_data(self, search=None, **kwargs):
        context = super(FileCategoryDetailView, self).get_context_data(**kwargs) # this adds the filecategory object to context[context_object_name]
        category = context['filecategory']

        # grab the category and sub category ids
        arr_sub_categories_ids = [context['filecategory'].pk]
        temp_subcats_ids = list(context['filecategory'].filecategory_set.current().values('pk'))

        while temp_subcats_ids: #IMPRV: fix this odd code - looping and consuming
            # add to our ids
            cat = temp_subcats_ids.pop()
            #print 'cat[pk]: %s' % cat['pk']
            arr_sub_categories_ids.append(cat['pk'])
            # add any children to our temp_subcats_ids
            children = FileCategory.objects.get(pk=cat['pk']).filecategory_set.current().values('pk')
            #print 'children: %s' % children
            temp_subcats_ids.extend(children)

        #print arr_sub_categories_ids
        #context['filecategory_files'] = context[self.context_object_name].file_set.active()
        context['filecategory_files'] = File.objects.active().filter(category__in=arr_sub_categories_ids)

        search_form = self.get_form_class()
        search_form_kwargs = self.get_form_kwargs()
        search_string = self.request.GET.get('search_text', '')
        search_string_arr = search_string.split(',')
        # filter based on search string if any
        while search_string_arr:
            search_chunk = search_string_arr.pop().strip()
            context['filecategory_files'] = context['filecategory_files'].filter(Q(name__icontains=search_chunk) |
                                                                                 Q(description__icontains=search_chunk) |
                                                                                 Q(tags__name__icontains=search_chunk)).distinct()
        context[self.form_name] = search_form(**search_form_kwargs) # the ** is to convert the dict into pure kwargs
        return context

    # request METHOD handlers
    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, search=getattr(kwargs, 'search', None))
        return self.render_to_response(context=context)


class FileSendView(PermissionRequiredMixin, SingleObjectMixin, View):
    """ 
    Sends a file from a FileField type field on a model instance using HttpResponse header 
    
    Since it extends SingleObjectMixin it looks for pk or slug in the url patterns.
    To use in your view you must specify ```file_field``` which is the name of FileField 
    attribute on model
    
    """
    ### settings
    file_field_name = 'file' # name of the field on model that is of File type and will be sent
    permission_required = 'filelibrary.view_file'


    ### overide/extend django methods
    def get_queryset(self):
        return File.objects.active()

    def get(self, request, *args, **kwargs):
        """ we are going to send the file directly to end user """
        instance = self.get_object()
        try:
            file = getattr(instance, self.file_field_name).file
        except AttributeError:
            raise ImproperlyConfigured(
                "FileSendView requires that 'file_field_name' be set to the name of a FileField on the model"
                )
        response = HttpResponse(file.read(), mimetype='application/%s' % (mimetypes.guess_type(file.name)[0]))
        response['Content-Disposition'] = 'attachment; filename=%s-%s' % (slugify(instance.name), file.name)# IMPRV: add actuall slug field to File
        return response
