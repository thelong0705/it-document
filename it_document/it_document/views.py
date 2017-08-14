from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView
from el_pagination.decorators import page_template
from document.models import Document


class IndexPage(TemplateView):
    template_name = 'index.html'


def search(request, keyword):
    return render(request, 'search.html', {'keyword': keyword})


@page_template('document/top_6_likes.html')
@page_template('document/top_6_rating.html', key='top_rating_page')
@page_template('document/top_6_latest.html', key='latest')
def entry_index(request, template='index.html', extra_context=None):
    context = {
        'documents': Document.objects.filter(approve=True).annotate(
            num_likes=Count('liked_by')
        ).order_by('-num_likes', '-rating', '-id')[:12],
        'documents_top_rating': Document.objects.annotate(
            num_votes=Count('userratedocument')
        ).filter(num_votes__gt=1, approve=True).order_by('-rating', '-num_votes', '-id')[:12],
        'documents_latest': Document.objects.filter(approve=True).order_by('-id')[:12]
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)