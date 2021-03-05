import itertools

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from django_tables2 import RequestConfig, tables

from app_create_chklst.forms import HeadingModelForm
from app_create_chklst.models import Heading, Category
from app_utilities.models import Translation
from app_utilities.views import render_col_del_generic, render_enable_generic


def head_mgmt_view(request):
    """
    view to call tables2 HeadingsMgmtTable
    could be a Listview - Maybe later
    """
    context = {'title': "Headings"}
    if request.method == 'POST':
        return render(request, "app_create_chklst/headingsmgmt.html", context=context)
    if request.method == 'GET':
        print("Ici")
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        if request.user.is_superuser:
            headings = Heading.objects.all().order_by('head_key')
        else:
            headings = Heading.objects.filter(head_company=request.user.user_company).order_by('head_key')

        headings_table = HeadingsMgmtTable(headings,
                                           request.user.preferred_language.code,
                                           request.user.pro, prefix="1-")

        RequestConfig(request, paginate={"per_page": 5}).configure(headings_table)
        context['headingtable'] = headings_table
        return render(request, "app_create_chklst/headingsmgmt.html", context=context)


class HeadingsMgmtTable(tables.Table):
    """
        Django tables2 for headings
        1st init columns --> attr class for css (witdh)
        __init__ --> define the headers. Because the translation : not in 1st init !
        render_cols for specificities of each col --> generic cols are in utilities
        The dialogboxes are launched via JS
    """
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#",
                                    attrs={'td': {'class': 'mgr_counter_col'}})
    col_del = tables.columns.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name="",
                                    attrs={'td': {'class': 'mgr_col_del_col'}})
    head_key = tables.columns.Column(attrs={'td': {'class': 'head_key_col'}})

    class Meta:
        model = Heading
        fields = ('counter', 'head_key', 'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        self.base_columns['head_key'].verbose_name = Translation.get_translation('Headings', language=args[1])
        super(HeadingsMgmtTable, self).__init__(*args, **kwargs)

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1

    def render_col_del(self, *args, **kwargs):
        var = render_col_del_generic(str(kwargs['record'].pk), self.request.user)
        return format_html(var)

    # noinspection PyMethodMayBeStatic
    def render_mgr_enable(self, *args, **kwargs):
        var = render_enable_generic(kwargs['value'])
        return format_html(var)

"""
All the modal view are from the BSModalview : https://github.com/trco/django-bootstrap-modal-forms
"""

class HeadingCreateView(BSModalCreateView):
    """
    Create category --> modal create View
    """
    template_name = 'app_create_chklst/dialogboxes/createheading.html'
    form_class = HeadingModelForm
    form = HeadingModelForm
    model = Heading
    success_message = 'CreateheadingOK'
    success_url = reverse_lazy('app_create_chklst:chk-headmgmt')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Createheading'
        context['create'] = True
        return context



class HeadingUpdateView(BSModalUpdateView):
    """
    Update category --> modal update view
    """
    model = Heading
    template_name = 'app_create_chklst/dialogboxes/createheading.html'
    form_class = HeadingModelForm
    success_message = 'UpdateheadingOK'
    success_url = reverse_lazy('app_create_chklst:chk-headmgmt')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Updateheading'
        context['create'] = False
        return context


class HeadingDeleteView(BSModalDeleteView):
    """
    Category Delete --> modal create view
    """
    template_name = 'app_create_chklst/dialogboxes/deleteheading.html'
    model = Heading
    success_message = 'DeleteheadingOK'
    success_url = reverse_lazy('app_create_chklst:chk-headmgmt')

    def post(self, request, pk):
        heading = Heading.objects.get(pk=pk)
        heading.delete()
        messages.success(request, self.success_message)
        return redirect(self.success_url)


class HeadingDisplayView(BSModalReadView):
    """
    Heading display --> modal display/read view
    """
    model = Heading
    template_name = 'app_create_chklst/dialogboxes/displayheading.html'