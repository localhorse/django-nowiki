from django.db import models
from django.contrib.auth.models import User

from templatetags.wiki import wikify

class PageRevision(models.Model):

    content = models.TextField()
    edit_reason = models.TextField(max_length = 100, null = True)
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add = 1)
    revision_for = models.ForeignKey('Page', null = True)
    revision_num = models.IntegerField(default = 0)

    def save(self):
        super(PageRevision, self).save()

    def __str__(self):
        return "%s revision (\"%s\")" % (self.revision_for.name, self.edit_reason)

    def get_absolute_url(self):
        return '/revision/%s/' % self.id

    class Admin:
        pass

class Page(models.Model):

    name = models.CharField(max_length=255, unique=True)
    
    created_on = models.DateTimeField(auto_now_add = 1)
    modified_on = models.DateTimeField(auto_now_add = 1)
    current_revision = models.ForeignKey(PageRevision, related_name = 'main', blank = True, null = True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        #self.rendered = wikify(self.content)
        super(Page, self).save(*args, **kwargs)
