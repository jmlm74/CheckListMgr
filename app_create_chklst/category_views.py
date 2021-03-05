import itertools

from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalReadView,
                                           BSModalUpdateView,
                                           BSModalDeleteView)
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from django_filters import FilterSet, ModelChoiceFilter, CharFilter
from django_tables2 import RequestConfig, tables
from sortable_listview import SortableListView

from app_create_chklst.forms import CategoryModelForm
from app_create_chklst.models import Category, Heading
from app_utilities.models import Translation
from app_utilities.views import render_col_del_generic, render_enable_generic

"""
All the modal view are from the BSModalview : https://github.com/trco/django-bootstrap-modal-forms
"""


class CategoryFilter(FilterSet):
    cat_heading = ModelChoiceFilter(field_name='cat_heading__head_key',
                                     queryset=Heading.objects.all())
    cat_key = CharFilter(field_name='line_key', lookup_expr='icontains')
    cat_wording = CharFilter(field_name='line_wording', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['cat_heading__head_key', 'cat_wording', 'cat_key']
        # fields = '__all__'
        # exclude = ['']


def category_mgmt_view(request):
    """
    view to call tables2 CategoryMgmtTable
    could be a Listview - Maybe later
    """
    context = {'title': "Categories"}
    if request.method == 'POST':
        return render(request, "app_create_chklst/categorymgmt.html", context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        if request.user.is_superuser:
            categories = Category.objects.all().order_by('cat_heading', 'cat_key')
        else:
            categories = Category.objects.filter(cat_company=request.user.user_company).\
                order_by('cat_heading', 'cat_key')
        myfilter = CategoryFilter(request.GET, queryset=categories)
        categories = myfilter.qs
        category_table = CategoryMgmtTable(categories,
                                           request.user.preferred_language.code,
                                           request.user.pro, prefix="1-")

        RequestConfig(request, paginate={"per_page": 15}).configure(category_table)
        context['categorytable'] = category_table
        context['myfilter'] = myfilter
        return render(request, "app_create_chklst/categorymgmt.html", context=context)


class CategoryMgmtTable(tables.Table):
    """
        Django tables2 for Categories
        1st init columns --> attr class for css (witdh)
        __init__ --> define the headers. Because the translation : not in 1st init !
        render_cols for specificities of each col --> generic cols are in utilities
        The dialogboxes are launched via JS
    """
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#",
                                    attrs={'td': {'class': 'cat_counter_col'}})
    col_del = tables.columns.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name="",
                                    attrs={'td': {'class': 'cat_col_del_col'}})
    cat_key = tables.columns.Column(attrs={'td': {'class': 'cat_key_col'}})
    cat_wording = tables.columns.Column(attrs={'td': {'class': 'cat_wording_col'}})
    cat_enable = tables.columns.Column(attrs={'td': {'class': 'cat_enable_col'}})
    cat_heading = tables.columns.Column(attrs={'td': {'class': 'cat_heading_col'}})

    class Meta:
        model = Category
        fields = ('counter', 'cat_heading', 'cat_key', 'cat_wording', 'cat_enable', 'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        self.base_columns['cat_heading'].verbose_name = Translation.get_translation('Heading', language=args[1])
        self.base_columns['cat_key'].verbose_name = Translation.get_translation('Key', language=args[1])
        self.base_columns['cat_wording'].verbose_name = Translation.get_translation('Wording', language=args[1])
        self.base_columns['cat_enable'].verbose_name = Translation.get_translation('Enable', language=args[1])
        super(CategoryMgmtTable, self).__init__(*args, **kwargs)

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1

    def render_col_del(self, *args, **kwargs):
        var = render_col_del_generic(str(kwargs['record'].pk), self.request.user)
        return format_html(var)

    # noinspection PyMethodMayBeStatic
    def render_line_enable(self, *args, **kwargs):
        var = render_enable_generic(kwargs['value'])
        return format_html(var)


class CategoryCreateView(BSModalCreateView):
    """
    Create category --> modal create View
    """
    template_name = 'app_create_chklst/dialogboxes/createcategory.html'
    form_class = CategoryModelForm
    form = CategoryModelForm
    success_message = 'CreatecatOK'
    success_url = reverse_lazy('app_create_chklst:chk-catmgmt')


class CategoryUpdateView(BSModalUpdateView):
    """
    Update category --> modal update view
    """
    model = Category
    template_name = 'app_create_chklst/dialogboxes/updatecategory.html'
    form_class = CategoryModelForm
    success_message = 'UpdatecatOK'
    success_url = reverse_lazy('app_create_chklst:chk-catmgmt')


class CategoryDeleteView(BSModalDeleteView):
    """
    Category Delete --> modal create view
    """
    template_name = 'app_create_chklst/dialogboxes/deletecategory.html'
    model = Category
    success_message = 'DeletecatOK'
    success_url = reverse_lazy('app_create_chklst:chk-catmgmt')

    def post(self, request, pk):
        category = Category.objects.get(pk=pk)
        if category.clc_categories.all().exists():
            messages.error(request, "Errdelcatchild")
        else:
            category.delete()
            messages.success(request, self.success_message)
        return redirect(self.success_url)


class CategoryDisplayView(BSModalReadView):
    """
    Category display --> modal display/read view
    """
    model = Category
    template_name = 'app_create_chklst/dialogboxes/displaycategory.html'


