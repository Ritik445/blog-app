
import django_filters
from .models import Blog

class BlogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    content = django_filters.CharFilter(lookup_expr='icontains', label='Content')

    class Meta:
        model = Blog
        fields = ['title', 'content']
