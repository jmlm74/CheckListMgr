import itertools

from django.contrib import messages
from django.shortcuts import render
from django.utils.html import format_html
from django_filters import FilterSet, CharFilter
from django_tables2 import RequestConfig, tables

from app_input_chklst.models import Material
from app_utilities.models import Translation
from app_utilities.views import render_col_del_generic, render_enable_generic


class MaterialFilter(FilterSet):
    mat_designation = CharFilter(field_name='mat_designation', lookup_expr='icontains')
    mat_registration = CharFilter(field_name='mat_registration', lookup_expr='icontains')
    mat_type = CharFilter(field_name='mat_type', lookup_expr='icontains')
    mat_model = CharFilter(field_name='mat_model', lookup_expr='icontains')
    mat_manager = CharFilter(field_name='mat_manager', lookup_expr='icontains')

    class Meta:
        model = Material
        fields = ['mat_designation', 'mat_registration', 'mat_type', 'mat_model', 'mat_manager', ]


def mat_mgmt_view(request):
    """
    view to call tables2 MgrMgmtTable
    could be a Listview - Maybe later
    """
    context = {'title': "Materials"}
    if request.method == 'POST':
        return render(request, "app_input_chklst/managermgmt.html", context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        if request.user.is_superuser:
            managers = Material.objects.all().order_by('mat_designation')
        else:
            managers = Material.objects.filter(mat_company=request.user.user_company).order_by('mat_designation')
        myfilter = MaterialFilter(request.GET, queryset=managers)
        materials = myfilter.qs
        mat_table = MatMgmtTable(materials,
                                 request.user.preferred_language.code,
                                 request.user.pro, prefix="1-")

        RequestConfig(request, paginate={"per_page": 5}).configure(mat_table)
        context['mattable'] = mat_table
        context['myfilter'] = myfilter
        return render(request, "app_input_chklst/maininput.html", context=context)


class MatMgmtTable(tables.Table):
    """
        Django tables2 for materials
        1st init columns --> attr class for css (witdh)
        __init__ --> define the headers. Because the translation : not in 1st init !
        render_cols for specificities of each col --> generic cols are in utilities
        The dialogboxes are launched via JS
    """
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#",
                                    attrs={'td': {'class': 'mat_counter_col'}})
    col_del = tables.columns.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name="",
                                    attrs={'td': {'class': 'mat_col_del_col'}})
    mat_designation = tables.columns.Column(attrs={'td': {'class': 'mat_designation_col'}})
    mat_registration = tables.columns.Column(attrs={'td': {'class': 'mat_registration_col'}})
    mat_type = tables.columns.Column(attrs={'td': {'class': 'mat_type_col'}})
    mat_model = tables.columns.Column(attrs={'td': {'class': 'mat_model_col'}})
    mat_enable = tables.columns.Column(attrs={'td': {'class': 'mat_enable_col'}})
    mat_manager = tables.columns.Column(attrs={'td': {'class': 'mat_manager_col'}})
    mat_material = tables.columns.Column(attrs={'td': {'class': 'mat_material_col'}})

    class Meta:
        model = Material
        fields = ('counter', 'mat_designation', 'mat_registration', 'mat_type', 'mat_model', 'mat_enable',
                  'mat_manager', 'mat_material', 'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        self.base_columns['mat_designation'].verbose_name = Translation.get_translation('Designation', language=args[1])
        self.base_columns['mat_registration'].verbose_name = Translation.get_translation('Serial/N', language=args[1])
        self.base_columns['mat_type'].verbose_name = Translation.get_translation('Type', language=args[1])
        self.base_columns['mat_model'].verbose_name = Translation.get_translation('Model', language=args[1])
        self.base_columns['mat_enable'].verbose_name = Translation.get_translation('Enable', language=args[1])
        self.base_columns['mat_manager'].verbose_name = Translation.get_translation('Manager', language=args[1])
        self.base_columns['mat_material'].verbose_name = Translation.get_translation('Materialprim', language=args[1])
        super(MatMgmtTable, self).__init__(*args, **kwargs)

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1

    def render_col_del(self, *args, **kwargs):
        var = render_col_del_generic(str(kwargs['record'].pk), self.request.user)
        return format_html(var)

    def render_mat_enable(self, *args, **kwargs):
        var = render_enable_generic(kwargs['value'])
        return format_html(var)
