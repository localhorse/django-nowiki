from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from forms import PageForm
from models import Page
from models import PageRevision

from datetime import datetime

def index(request):
    """Lists all pages stored in the wiki."""
    pages = Page.objects.all()

    for page in pages:
        # turn underscores to spaces
        page.space_name = page.name.replace("_", " ")

    context = RequestContext(request)
    return render_to_response('wiki/index.html', {'pages': pages}, context)

def history(request, name):
    """Lists all page edits for this page."""
    page = Page.objects.get(name = name)
    # order by date, current revision on top
    page_revisions = PageRevision.objects.filter(revision_for = page).order_by("-created_on").exclude(id = page.current_revision.id)
    current_revision = PageRevision.objects.get(id = page.current_revision.id)
    # turn underscores to spaces
    page.space_name = page.name.replace("_", " ")

    context = RequestContext(request)
    return render_to_response('wiki/history.html', {'page': page, 'page_revisions': page_revisions, 'current_revision': current_revision}, context)

def old_page(request, name, id):
    """Displays a specific page revision."""
    page_revision = PageRevision.objects.get(id = id)
    page = Page.objects.get(id = page_revision.revision_for_id)
    # take out underscores
    page.space_name = page.name.replace("_", " ")
    context = RequestContext(request)
    return render_to_response('wiki/revision.html', {'page': page, 'page_revision': page_revision}, context)

@staff_member_required
def delete_page(request, name):
    """Delete a specific page"""
    page = Page.objects.get(name = name)
    context = RequestContext(request)
    page.space_name = page.name.replace("_", " ")

    if request.method == 'POST':
        submitted = True
        if request.POST.__getitem__('confirm') == "Yes":
            confirmed = True
            page.delete()
        else:
            confirmed = None
    else:
        submitted = False
        confirmed = None

    return render_to_response('wiki/delete.html', {'page': page, 'submitted': submitted, 'confirmed': confirmed}, context)

@staff_member_required
def revert_page(request, name, id):
    """Reverts the current page to a specific revision."""
    page_revision = PageRevision.objects.get(id = id)
    page = Page.objects.get(id = page_revision.revision_for_id)
    # take out underscores
    page.space_name = page.name.replace("_", " ")
    context = RequestContext(request)

    if request.method == 'POST':
        submitted = True
        # this doesn't seem to be a good way to do this...
        # but I'm not sure how else to get the info on
        # this particular type of form.
        if request.POST.__getitem__('confirm') == "Yes":
            confirmed = True
            page.current_revision = page_revision
            page.modified_on = datetime.now()
            page.user = request.user
            page.save()
        else:
            confirmed = None
    else:
        submitted = False
        confirmed = None

    return render_to_response('wiki/revert.html', {'page': page, 'page_revision': page_revision, 'submitted': submitted, 'confirmed': confirmed}, context)

def view(request, name):
    """Shows a single wiki page."""

    try:
        page = Page.objects.get(name=name)
        current_revision = PageRevision.objects.get(id = page.current_revision.id)
    except Page.DoesNotExist:
        page = Page(name=name)
        current_revision = None

    # take out underscores
    page.space_name = page.name.replace("_", " ")

    context = RequestContext(request)
    return render_to_response('wiki/view.html', {'page': page, 'current_revision': current_revision}, context)


@csrf_protect
@staff_member_required
def edit(request, name):
    """Allows users to edit wiki pages."""
    try:
        page = Page.objects.get(name=name)
    except Page.DoesNotExist:
        page = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if not page:
                # it's a new page
                page = Page()

                page.name = form.cleaned_data['name']

                page.user = request.user
                page.created_on = datetime.now()
                page.save()

                page_revision = PageRevision(content = form.cleaned_data['content'], edit_reason = form.cleaned_data['edit_reason'], user = request.user, revision_for = page)
                page_revision.save()

                page.current_revision = page_revision
                page.save()

            else:
                # it's an edit on an old page

                page.name = form.cleaned_data['name']

                revision_count = PageRevision.objects.filter(revision_for = page).count()
                new_rev = revision_count + 1
                page_revision = PageRevision(content = form.cleaned_data['content'], edit_reason = form.cleaned_data['edit_reason'], user = request.user, revision_for = page, revision_num = new_rev)
                page_revision.save()

                page.current_revision = page_revision
                page.modified_on = datetime.now()
                page.user = request.user
                page.save()
            
            return HttpResponseRedirect('../../%s/' % page.name)
    else:
        if page:
            page_dict = page.__dict__
            # we have phased out page.content,
            # instead page will be a reference to current revision content.
            # but for the purposes of the form, we'll emulate it (ugly hack!)
            page_dict['content'] = page.current_revision.content
            form = PageForm(initial=page_dict)
        else:
            form = PageForm(initial={'name': name})

    context = RequestContext(request)
    return render_to_response('wiki/edit.html', {'form': form}, context)
