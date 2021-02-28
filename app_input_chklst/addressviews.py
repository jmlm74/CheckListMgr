import itertools

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView, BSModalUpdateView, BSModalDeleteView
from django_tables2 import RequestConfig, tables

from django.contrib import messages
from django.db.models import RestrictedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.html import format_html
from django_filters import FilterSet, CharFilter

from app_input_chklst.forms import AddressCreateForm
from app_user.models import Address
from app_utilities.models import Translation
from app_utilities.views import render_enable_generic, render_col_del_generic


class AddressFilter(FilterSet):
    zipcode = CharFilter(field_name='zipcode', lookup_expr='icontains')
    address_name = CharFilter(field_name='address_name', lookup_expr='icontains')

    class Meta:
        model = Address
        fields = ['zipcode']


def addr_mgmt_view(request):
    """
    view to call tables2 AddrMgmtTable
    could be a Listview - Maybe later
    """
    context = {'title': "Addresses"}
    if request.method == 'POST':
        return render(request, "app_input_chklst/addressmgmt.html", context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        addresses = Address.objects.all().order_by('address_name')
        myfilter = AddressFilter(request.GET, queryset=addresses)
        addresses = myfilter.qs
        if request.user.is_superuser:
            addr_table = AddrMgmtTable(addresses,
                                       request.user.preferred_language.code,
                                       request.user.pro, prefix="1-")

        else:
            addr_table = AddrMgmtTable(addresses,
                                       request.user.preferred_language.code,
                                       request.user.pro, prefix="1-")

        RequestConfig(request, paginate={"per_page": 5}).configure(addr_table)

        context['addrtable'] = addr_table
        context['myfilter'] = myfilter
        return render(request, "app_input_chklst/addressmgmt.html", context=context)


class AddrMgmtTable(tables.Table):
    """
        Django tables2 for Addresses
        1st init columns --> attr class for css (witdh)
        __init__ --> define the headers. Because the translation : not in 1st init !
        render_cols for specificities of each col --> generic cols are in utilities
        The dialogboxes are launched via JS
    """
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#",
                                    attrs={'td': {'class': 'addr_counter_col'}})
    col_del = tables.columns.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name="",
                                    attrs={'td': {'class': 'addr_col_del_col'}})
    address_name = tables.columns.Column(attrs={'td': {'class': 'addr_name_col'}})
    street_number = tables.columns.Column(attrs={'td': {'class': 'addr_num_col'}})
    street_type = tables.columns.Column(attrs={'td': {'class': 'addr_type_col'}})
    address1 = tables.columns.Column(attrs={'td': {'class': 'addr_addr1_col'}})
    address2 = tables.columns.Column(attrs={'td': {'class': 'addr_addr2_col'}})
    zipcode = tables.columns.Column(attrs={'td': {'class': 'addr_zip_col'}})
    city = tables.columns.Column(attrs={'td': {'class': 'addr_city_col'}})

    class Meta:
        # model = Address
        fields = ('counter', 'address_name', 'street_number', 'street_type', 'address1', 'address2',
                  'zipcode', 'city', 'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        self.base_columns['address_name'].verbose_name = Translation.get_translation('Address', language=args[1])
        self.base_columns['street_number'].verbose_name = Translation.get_translation('Street_number', language=args[1])
        self.base_columns['street_type'].verbose_name = Translation.get_translation('Street_type', language=args[1])
        self.base_columns['address1'].verbose_name = Translation.get_translation('Address1', language=args[1])
        self.base_columns['address2'].verbose_name = Translation.get_translation('Address2', language=args[1])
        self.base_columns['zipcode'].verbose_name = Translation.get_translation('Zipcode', language=args[1])
        self.base_columns['city'].verbose_name = Translation.get_translation('City', language=args[1])
        super(AddrMgmtTable, self).__init__(*args, **kwargs)

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1

    def render_col_del(self, *args, **kwargs):
        var = render_col_del_generic(str(kwargs['record'].pk), self.request.user)
        return format_html(var)

    def render_mgr_enable(self, *args, **kwargs):
        var = render_enable_generic(kwargs['value'])
        return format_html(var)


class AddressCreateView(BSModalCreateView):
    """
    Create manager --> modal View
    """
    template_name = 'app_input_chklst/dialogboxes/createaddress.html'
    form_class = AddressCreateForm
    form = AddressCreateForm
    success_message = 'CreateadrOK'
    success_url = reverse_lazy('app_input_chklst:inp-addrmgmt')

    def get_context_data(self, **kwargs):
        context = super(AddressCreateView, self).get_context_data(**kwargs)
        context['title'] = "Createaddr"
        context['btn'] = "Create"
        return context


class AddressUpdateView(BSModalUpdateView):
    """
    Update manager --> modal view
    """
    model = Address
    template_name = 'app_input_chklst/dialogboxes/createaddress.html'
    form_class = AddressCreateForm
    success_message = 'UpdateaddrOK'
    success_url = reverse_lazy('app_input_chklst:inp-addrmgmt')

    def get_context_data(self, **kwargs):
        context = super(AddressUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Updateaddr"
        context['btn'] = "Update"
        return context


class AddressDisplayView(BSModalReadView):
    """
    Manager display --> modal view
    """
    model = Address
    template_name = 'app_input_chklst/dialogboxes/displayaddress.html'

    def get_context_data(self, **kwargs):
        context = super(AddressDisplayView, self).get_context_data(**kwargs)
        context['title'] = "Displayaddr"
        return context


class AddressDeleteView(BSModalDeleteView):
    """
    Manager Delete --> modal view
    """
    template_name = 'app_input_chklst/dialogboxes/deleteaddr.html'
    model = Address
    success_message = 'DeleteaddrOK'
    error_message = "DeleteaddrKO"
    success_url = reverse_lazy('app_input_chklst:inp-addrmgmt')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
            messages.success(request, self.success_message)
        except RestrictedError:
            messages.error(request, self.error_message)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(AddressDeleteView, self).get_context_data(**kwargs)
        context['title'] = "Deleteaddr"
        return context