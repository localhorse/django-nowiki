from django import forms as forms

from models import Page


class PageForm(forms.Form):
    name = forms.CharField(max_length=255)
    content = forms.CharField(widget=forms.Textarea())
    edit_reason = forms.CharField(max_length = 100, initial = "")

    def clean_name(self):
        import re
        #from templatetags.wiki import WIKI_WORD
        from templatetags.wiki import VALID_TITLE

        #pattern = re.compile(WIKI_WORD)
        pattern = re.compile(VALID_TITLE)

        name = self.cleaned_data['name']
        if not pattern.match(name):
            #raise forms.ValidationError('Must be a WikiWord.')
            raise forms.ValidationError('Page title must start with alphanumeric character, and contain only underscores or alphanumeric characters.')
        return name

