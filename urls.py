from django.conf.urls.defaults import *

#from templatetags.wiki import WIKI_WORD
from templatetags.wiki import VALID_TITLE

urlpatterns = patterns('wiki.views',
    (r'^$', 'index'),
    #('(?P<name>%s)/$' % WIKI_WORD, 'view'),
    #('(?P<name>%s)/edit/$' % WIKI_WORD, 'edit'),
    ('(?P<name>%s)/$' % VALID_TITLE, 'view'),
    ('(?P<name>%s)/edit/$' % VALID_TITLE, 'edit'),
    ('(?P<name>%s)/history/$' % VALID_TITLE, 'history'),
    ('(?P<name>%s)/revision/(?P<id>\d+)/$' % VALID_TITLE, 'old_page'),
    ('(?P<name>%s)/revert/(?P<id>\d+)/$' % VALID_TITLE, 'revert_page'),
    ('(?P<name>%s)/delete/$' % VALID_TITLE, 'delete_page'),
)
