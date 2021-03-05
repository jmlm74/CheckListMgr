import itertools

from bootstrap_modal_forms.generic import BSModalCreateView, \
    BSModalUpdateView, \
    BSModalDeleteView, \
    BSModalReadView
from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from django_filters import FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter
from django_tables2 import RequestConfig, tables

from app_create_chklst.forms import LineModelForm
from app_create_chklst.models import Line, Heading
from app_utilities.models import Translation
from app_utilities.views import render_col_del_generic, render_enable_generic


class LineFilter(FilterSet):
    line_heading = ModelChoiceFilter(field_name='line_heading__head_key',
                                     queryset=Heading.objects.all())
    line_key = CharFilter(field_name='line_key', lookup_expr='icontains')
    line_wording = CharFilter(field_name='line_wording', lookup_expr='icontains')

    class Meta:
        model = Line
        fields = ['line_heading__head_key', 'line_wording', 'line_key', 'line_type']


def line_mgmt_view(request):
    """
    view to call tables2 LinesMgmtTable
    could be a Listview - Maybe later
    """
    context = {'title': "Lines"}
    if request.method == 'POST':
        return render(request, "app_create_chklst/linemgmt.html", context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        if request.user.is_superuser:
            lines = Line.objects.all().order_by('line_heading', 'line_key')
        else:
            lines = Line.objects.filter(line_company=request.user.user_company).order_by('line_heading', 'line_key')
        myfilter = LineFilter(request.GET, queryset=lines)
        lines = myfilter.qs
        lines_table = LinesMgmtTable(lines,
                                     request.user.preferred_language.code,
                                     request.user.pro, prefix="1-")

        RequestConfig(request, paginate={"per_page": 15}).configure(lines_table)
        context['linetable'] = lines_table
        context['myfilter'] = myfilter
        return render(request, "app_create_chklst/linemgmt.html", context=context)


class LinesMgmtTable(tables.Table):
    """
        Django tables2 for lines
        1st init columns --> attr class for css (witdh)
        __init__ --> define the headers. Because the translation : not in 1st init !
        render_cols for specificities of each col --> generic cols are in utilities
        The dialogboxes are launched via JS
    """
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#",
                                    attrs={'td': {'class': 'line_counter_col'}})
    col_del = tables.columns.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name="",
                                    attrs={'td': {'class': 'line_col_del_col'}})
    line_key = tables.columns.Column(attrs={'td': {'class': 'line_key_col'}})
    line_wording = tables.columns.Column(attrs={'td': {'class': 'line_wording_col'}})
    line_enable = tables.columns.Column(attrs={'td': {'class': 'line_enable_col'}})
    line_type = tables.columns.Column(attrs={'td': {'class': 'line_type_col'}})
    line_heading = tables.columns.Column(attrs={'td': {'class': 'line_heading_col'}})

    class Meta:
        model = Line
        fields = ('counter', 'line_heading', 'line_key', 'line_wording', 'line_enable', 'line_type',  'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        self.base_columns['line_heading'].verbose_name = Translation.get_translation('Heading', language=args[1])
        self.base_columns['line_key'].verbose_name = Translation.get_translation('Key', language=args[1])
        self.base_columns['line_wording'].verbose_name = Translation.get_translation('Wording', language=args[1])
        self.base_columns['line_enable'].verbose_name = Translation.get_translation('Enable', language=args[1])
        self.base_columns['line_type'].verbose_name = Translation.get_translation('Type', language=args[1])
        super(LinesMgmtTable, self).__init__(*args, **kwargs)

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


class LineCreateView(BSModalCreateView):
    """
    Create line --> modal create View
    """
    template_name = 'app_create_chklst/dialogboxes/createline.html'
    form_class = LineModelForm
    form = LineModelForm
    success_message = 'LineCreateOK'
    success_url = reverse_lazy('app_create_chklst:chk-linemgmt')


class LineDeleteView(BSModalDeleteView):
    """
    Line delete --> modal delete view
    """
    template_name = 'app_create_chklst/dialogboxes/deleteline.html'
    model = Line
    success_message = 'LineDeleteOK'
    success_url = reverse_lazy('app_create_chklst:chk-linemgmt')

    def post(self, request, pk):
        line = Line.objects.get(pk=pk)
        if line.cll_lines.all().exists():
            messages.error(request, "Errdellinechild")
        else:
            line.delete()
            messages.success(request, self.success_message)
        return redirect(self.success_url)


class LineUpdateView(BSModalUpdateView):
    """
    Line update --> modal update view
    """
    model = Line
    template_name = 'app_create_chklst/dialogboxes/updateline.html'
    form_class = LineModelForm
    success_message = 'LineUpdateOK'
    success_url = reverse_lazy('app_create_chklst:chk-linemgmt')


class LineDisplayView(BSModalReadView):
    """
    Line display --> modal display/read view
    """
    model = Line
    template_name = 'app_create_chklst/dialogboxes/displayline.html'
