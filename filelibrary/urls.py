from django.conf.urls.defaults import patterns, include, url
from filelibrary.views import FileCategoryDetailView, FileCategoryIndexView, FileSendView

urlpatterns = patterns('', # prefix for any view referenced
    # Examples:
    # url(r'^$', 'index', name='index'),
    url(r'^$', FileCategoryIndexView.as_view(), name='FileCategoryIndexView'),
    url(r'^send-file-(?P<pk>\d+)/$', FileSendView.as_view(), name='FileSendView'),
    url(r'^(?P<slug_path>[-_\/\w]+)/$', FileCategoryDetailView.as_view(), name='FileCategoryDetailView'),


)

