import itertools

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView, BSModalUpdateView, BSModalDeleteView
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import format_html
from django_tables2 import tables, A, RequestConfig
from django_filters import FilterSet, CharFilter

from django.contrib import messages
from django.db.models import Q, RestrictedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from app_input_chklst.forms import ManagerCreateForm
from app_input_chklst.models import Manager
from app_utilities.models import Translation
from app_utilities.views import render_col_del_generic, render_enable_generic


class AddressFilter(FilterSet):
    mgr_name = CharFilter(field_name='mgr_name', lookup_expr='icontains')
    mgr_contact = CharFilter(field_name='mgr_contact', lookup_expr='icontains')
    mgr_email1 = CharFilter(field_name='mgr_email1', lookup_expr='icontains')
    mgr_company = CharFilter(field_name='mgr_company', lookup_expr='icontains')

    class Meta:
        model = Manager
        fields = ['mgr_name', 'mgr_contact', 'mgr_email1', 'mgr_company',]


def mgr_mgmt_view(request):
    """
    view to call tables2 MgrMgmtTable
    could be a Listview - Maybe later
    """
    context = {'title': "Managers"}
    if request.method == 'POST':
        return render(request, "app_input_chklst/managermgmt.html", context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        if request.user.is_superuser:
            managers = Manager.objects.all().order_by('mgr_name')
        else:
            managers = Manager.objects.filter(mgr_company=request.user.user_company).order_by('mgr_name')
        myfilter = AddressFilter(request.GET, queryset=managers)
        managers = myfilter.qs
        mgr_table = MgrMgmtTable(managers,
                                 request.user.preferred_language.code,
                                 request.user.pro, prefix="1-")

        RequestConfig(request, paginate={"per_page": 5}).configure(mgr_table)
        context['mgrtable'] = mgr_table
        context['myfilter'] = myfilter
        return render(request, "app_input_chklst/managermgmt.html", context=context)


class MgrMgmtTable(tables.Table):
    """
        Django tables2 for managers
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
    mgr_name = tables.columns.Column(attrs={'td': {'class': 'mgr_name_col'}})
    mgr_contact = tables.columns.Column(attrs={'td': {'class': 'mgr_contact_col'}})
    mgr_phone = tables.columns.Column(attrs={'td': {'class': 'mgr_phone_col'}})
    mgr_email1 = tables.columns.Column(attrs={'td': {'class': 'mgr_email_col'}})
    mgr_email2 = tables.columns.Column(attrs={'td': {'class': 'mgr_email_col'}})
    mgr_enable = tables.columns.Column(attrs={'td': {'class': 'mgr_enable_col'}})

    class Meta:
        model = Manager
        fields = ('counter', 'mgr_name', 'mgr_contact', 'mgr_phone', 'mgr_email1', 'mgr_email2',
                  'mgr_enable', 'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        self.base_columns['mgr_name'].verbose_name = Translation.get_translation('Manager', language=args[1])
        self.base_columns['mgr_contact'].verbose_name = Translation.get_translation('Contactname', language=args[1])
        self.base_columns['mgr_phone'].verbose_name = Translation.get_translation('Phone', language=args[1])
        self.base_columns['mgr_email1'].verbose_name = Translation.get_translation('Email1', language=args[1])
        self.base_columns['mgr_email2'].verbose_name = Translation.get_translation('Email2', language=args[1])
        self.base_columns['mgr_enable'].verbose_name = Translation.get_translation('Enable', language=args[1])
        super(MgrMgmtTable, self).__init__(*args, **kwargs)

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1

    def render_col_del(self, *args, **kwargs):
        var = render_col_del_generic(str(kwargs['record'].pk), self.request.user)
        return format_html(var)

    def render_mgr_enable(self, *args, **kwargs):
        var = render_enable_generic(kwargs['value'])
        return format_html(var)


class ManagerCreateView(BSModalCreateView):
    """
    Create manager --> modal create View
    """
    template_name = 'app_input_chklst/dialogboxes/createmanager.html'
    form_class = ManagerCreateForm
    form = ManagerCreateForm
    success_message = 'CreatemgrOK'
    success_url = reverse_lazy('app_input_chklst:inp-mgrmgmt')

    def get_success_url(self):
        url = self.request.GET.get('url', None)
        if url:
            return url
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super(ManagerCreateView, self).get_context_data(**kwargs)
        context['title'] = "Createmgr"
        context['btn'] = "Create"
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        # Test if Ajax --> Bug or pb with BS-Modal and file upload !
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # print(request.POST)
            # print(request.FILES)
            if form.is_valid():
                manager = Manager()
                save_manager(manager, form)
        return super().post(request, *args, **kwargs)


class ManagerDisplayView(BSModalReadView):
    """
    Manager display --> modal display/read view
    """
    model = Manager
    template_name = 'app_input_chklst/dialogboxes/displaymanager.html'

    def get_context_data(self, **kwargs):
        context = super(ManagerDisplayView, self).get_context_data(**kwargs)
        context['title'] = "Displaymgr"
        return context


class ManagerUpdateView(BSModalUpdateView):
    """
    Update manager --> modal update view
    """
    model = Manager
    template_name = 'app_input_chklst/dialogboxes/createmanager.html'
    form_class = ManagerCreateForm
    success_message = 'UpdatemgrOK'
    success_url = reverse_lazy('app_input_chklst:inp-mgrmgmt')

    def get_context_data(self, *arks, **kwargs):
        context = super(ManagerUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Updatemgr"
        context['btn'] = "Update"
        manager = Manager.objects.get(pk=self.kwargs['pk'])
        context['manager'] = manager
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        # Test if Ajax --> Bug or pb with BS-Modal and file upload !
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # print(request.POST)
            # print(request.FILES)
            if form.is_valid():
                manager = Manager.objects.get(pk=kwargs['pk'])
                save_manager(manager, form)
        return super().post(request, *args, **kwargs)


class ManagerDeleteView(BSModalDeleteView):
    """
    Manager Delete --> modal delete view
    """
    template_name = 'app_input_chklst/dialogboxes/deletemgr.html'
    model = Manager
    success_message = 'DeletemgrOK'
    error_message = 'DeletemgrKO'
    success_url = reverse_lazy('app_input_chklst:inp-mgrmgmt')

    def get_context_data(self, *arks, **kwargs):
        context = super(ManagerDeleteView, self).get_context_data(**kwargs)
        context['title'] = "Deletemgr"
        return context

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
            messages.success(request, self.success_message)
        except RestrictedError:
            messages.error(request, self.error_message)
        return redirect(self.success_url)


def save_manager(manager, form):
    """
    Save or update new manager from update or create form
    """
    manager.mgr_name = form.cleaned_data['mgr_name']
    manager.mgr_contact = form.cleaned_data['mgr_contact']
    manager.mgr_phone = form.cleaned_data['mgr_phone']
    manager.mgr_email1 = form.cleaned_data['mgr_email1']
    manager.mgr_email2 = form.cleaned_data['mgr_email2']
    if form.cleaned_data['mgr_enable'] == 'on':
        manager.mgr_enable = True
    else:
        manager.mgr_enable = False
    manager.mgr_lang = form.cleaned_data['mgr_lang']
    if form.cleaned_data['mgr_company']:
        manager.mgr_company = form.cleaned_data['mgr_company']
    manager.mgr_address = form.cleaned_data['mgr_address']
    try:
        if form.data['mgr_logo-clear'] == 'on':
            manager.mgr_logo = None
    except MultiValueDictKeyError:
        if form.cleaned_data['mgr_logo']:
            manager.mgr_logo = form.cleaned_data['mgr_logo']
    manager.save()
