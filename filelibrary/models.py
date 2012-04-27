from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import messages
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from urlparse import urlparse


class FileCategoryManager(models.Manager):
    """
    Adds additional commands to our objects manager:
    
    ```<foo>.objects.active()``` - all active slides
    """
    ### File Category Types
    TYPE_CHOICES = (
        ("general", "General"),
        #(100, "Photos"),
        ("videos", "Videos"),
    )
    ### Model (db table) wide constants - we put these and not in model definition to avoid circular imports.
    ### One can access these constants through <foo>.objects.STATUS_DISABLED or ImageManager.STATUS_DISABLED
    STATUS_DISABLED = 0
    STATUS_ENABLED = 100
    STATUS_ARCHIVED = 500
    STATUS_CHOICES = (
        (STATUS_DISABLED, "Disabled"),
        (STATUS_ENABLED, "Enabled"),
        (STATUS_ARCHIVED, "Archived"),
    )
    # we keep status and filters naming a little different as
    # it is not one-to-one mapping in all situations
    def live(self):
        """ Returns all entries accessible through front end site"""
        return self.all().filter(status=self.STATUS_ENABLED)
    def current(self):
        """ Returns entries that are live and considered 'fresh' """
        return self.all().filter(status=self.STATUS_ENABLED)
    def retired(self):
        """ Returns entries that are live and considered 'old' """
        return self.all().filter(status=self.STATUS_ARCHIVED)

class FileCategory(models.Model):
    """
    A file category - think of it like a basic Directory on a file system
    """
    ### model options
    class Meta:
        #ordering = ['parent_category', 'order']
        unique_together = [['parent_category', 'slug'], ['parent_category', 'name']] # parent_category and slug are used for one to one url mapping
                                                                                     # ex /category1/category2/category3/
        verbose_name_plural = 'File categories'
        ordering = ['name']
        permissions = [("view_filecategory", "Can view file category")] #

    ### django functions overrides
    def __unicode__(self):
        if self.parent_category and not self.parent_category == self:
            return u'%s > %s' % (self.parent_category, self.name)
        else:
            return u'%s' % (self.name,)

    def clean(self):
        """
        Following checks are performed before instance is saved:
        
        1. For SQLite checks that we do not a duplicate category with None parent and same Name 
           This is because the SQLITE allows this condition even though we have 
              unique_together specified
              FIXME: if not on sqlite than remove this check
              
        2. That a category points to itself as parent_category
        
        """
        if self.parent_category == None and FileCategory.objects.exclude(pk=self.pk).filter(name=self.name).exists():
            raise ValidationError("Another file category with name '%s' and parent category '%s' already exists" % (self.name, None))
        if self.parent_category == None and FileCategory.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
            raise ValidationError("Another file category with slug '%s' and parent category '%s' already exists" % (self.slug, None))
        if self.parent_category == self:
            raise ValidationError("A file category can not have itself as a 'Parent category'")

    def get_absolute_url(self):
        url = self.slug
        category = self.parent_category
        while category:
            url = u'%s/%s' % (urlquote(category.slug), url)
            category = category.parent_category
        return reverse('FileCategoryDetailView', kwargs={'slug_path': url}).replace('%20%3E%20', '/') #re-insert / back into the string

    ### custom managers
    objects = FileCategoryManager()
    status = models.IntegerField(choices=FileCategoryManager.STATUS_CHOICES, default=FileCategoryManager.STATUS_ENABLED)
    parent_category = models.ForeignKey('FileCategory', blank=True, null=True)
    template = models.CharField(max_length=100, choices=FileCategoryManager.TYPE_CHOICES)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, verbose_name='Page Url', help_text='ex. human-resources',)
    description = models.TextField(blank=True)

class FileManager(models.Manager):
    """
    Adds additional commands to our objects manager:
    
    Slide.objects.active() - all active slides
    """
    ### Model (db table) wide constants - we put these and not in model definition to avoid circular imports.
    ### One can access these constants through <foo>.objects.STATUS_DISABLED or ImageManager.STATUS_DISABLED
    STATUS_DISABLED = 0
    STATUS_ENABLED = 100
    STATUS_ARCHIVED = 500
    STATUS_CHOICES = (
        (STATUS_DISABLED, "Disabled"),
        (STATUS_ENABLED, "Enabled"),
        (STATUS_ARCHIVED, "Archived"),
    )
    # we keep status and filters naming a little different as
    # it is not one-to-one mapping in all situations
    def live(self):
        """ Returns all entries accessible through front end site"""
        return self.all().filter(status=self.STATUS_ENABLED)
    def active(self):
        """ Returns entries that are live and considered 'fresh' """
        return self.all().filter(status=self.STATUS_ENABLED)
    def retired(self):
        """ Returns entries that are live and considered 'old' """
        return self.all().filter(status=self.STATUS_ARCHIVED)

class File(models.Model):
    """
    Model that holds any type of file
    """
    ### model options
    class Meta:
       ordering = ['name']
       permissions = [("view_file", "Can view file")] #

    def get_absolute_url(self):
        return reverse('FileSendView', kwargs={'pk': self.pk})

    ### django function overrides
    def __unicode__(self):
        return self.name

    ### model functions
    def get_upload_path(instance, filename):
        """ returns a dynamic path for filefields/imagefieds """
        return '%s/%s/%s' % (instance._meta.app_label, instance._meta.module_name, filename)

    ### custom managers
    objects = FileManager()
    tags = TaggableManager(blank=True)

    ### model fields
    status = models.IntegerField(choices=FileManager.STATUS_CHOICES, default=FileManager.STATUS_ENABLED)
    file = models.FileField(upload_to="filelibrary/files", help_text='')
    category = models.ForeignKey(FileCategory, help_text='Select what category to store the file under')

    name = models.CharField(max_length=50)
    description = models.TextField(help_text='Short description of file. This text will be examined during search queries.')

