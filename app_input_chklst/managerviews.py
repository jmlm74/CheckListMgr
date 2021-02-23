from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView, BSModalUpdateView, BSModalDeleteView
from django.utils.datastructures import MultiValueDictKeyError
from sortable_listview import SortableListView

from django.contrib import messages
from django.db.models import Q, RestrictedError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from app_input_chklst.forms import ManagerCreateForm
from app_input_chklst.models import Manager


class MgrMgmtView(SortableListView):
    """
    List managers --> list sortable
    """
    context = {'title': 'Managers'}
    template_name = "app_input_chklst/managermgmt.html"
    context_object_name = "managers"
    allowed_sort_fields = {"mgr_name": {'default_direction': '', 'verbose_name': 'Manager'},
                           "mgr_contact": {'default_direction': '', 'verbose_name': 'Contactname'},
                           "mgr_phone": {'default_direction': '', 'verbose_name': 'Phone'},
                           "mgr_email1": {'default_direction': '', 'verbose_name': 'Email1'},
                           "mgr_email2": {'default_direction': '', 'verbose_name': 'Email2'},
                           "mgr_enable": {'default_direction': '', 'verbose_name': 'Enable'}, }
    default_sort_field = 'mgr_name'  # mandatory
    paginate_by = 5

    def get_queryset(self):
        order = self.request.GET.get('sort', 'mgr_name')

        if self.request.user.is_superuser:
            return Manager.objects.all().order_by(order)
        else:
            return Manager.objects.filter(Q(mgr_company=self.request.user.user_company)).order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', 'mgr_name')
        context['title'] = 'Managers'
        return context


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
