import itertools
import json

from django.contrib.auth import authenticate, login
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib import messages
from django_tables2 import tables, RequestConfig, A
from django.utils.html import format_html

from sortable_listview import SortableListView


from app_checklist.models import CheckListDone
from app_create_chklst.models import CheckList
from app_input_chklst.models import Material, Manager
from app_user.forms import UserCheckListMgrFormLogin
from app_utilities.models import Translation

language = "UK"


class Index(View):
    """
    Home page view --> Login form + geolocalisation (js) + weather report (js)
    """
    context = {'title': "app_user-home-title"}
    template_name = 'app_home/home.html'
    form = UserCheckListMgrFormLogin

    def get(self, request):
        try:
            request.session['language']
        except KeyError:
            request.session['language'] = 'UK'
        self.context['form'] = self.form(None)
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            bot = request.POST['bot_catcher']
            if len(bot):
                print("BOT-CATCHER !!!")  # Bot cather to use later with fail2ban ie
                self.context['form'] = self.form
                return render(request, 'bot-catcher.html')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    print(f"Connection of {username}")  # for the logs
                    request.session['language'] = str(user.preferred_language)
                    return HttpResponseRedirect(reverse('app_home:main'))  # return to the index
                else:
                    form.add_error(None, "Userdisabled")
            else:
                # a message to be used with fail2ban later
                print(f"Someone try to login and failed ! user : {username} - psw : {password}")
                form.add_error(None, "Userpswinvalid")
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('app_home:main'))
        self.context['form'] = form
        return render(request, self.template_name, context=self.context)


class LegalView(TemplateView):
    """
    display legal
    """
    template_name = "app_home/legal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Legal'
        return context


class ContactView(TemplateView):
    """
    display contact view
    """
    template_name = "app_home/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact'
        return context


class MainView(SortableListView):
    """
    The main view
    2 steps : The sortable list of the checklist you can input
            : The list of the checklist already input (limit 15)
    The sortable list is set in the def_queryset
    The check-lists are obtained in the get context data
    """
    context = {'title': 'Main'}
    template_name = "app_home/main.html"
    context_object_name = "checklists"
    allowed_sort_fields = {"chk_key": {'default_direction': '', 'verbose_name': 'Key'},
                           "chk_title": {'default_direction': '', 'verbose_name': 'Wording'},
                           }
    default_sort_field = 'chk_key'  # mandatory
    paginate_by = 5

    def get_queryset(self):
        order = self.request.GET.get('sort', 'chk_key')
        if self.request.user.is_superuser:
            return CheckList.objects.all().order_by(order)
        else:
            return CheckList.objects.filter(Q(chk_company=self.request.user.user_company) |
                                            Q(chk_company=999999) & Q(chk_enable=True)).order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', 'chk_key')
        context['title'] = 'Main'
        if self.request.user.is_superuser:
            checklistsdone = CheckListDone.objects.filter(cld_status=1).order_by('-modified_date')[:20]
        else:
            checklistsdone = CheckListDone.objects.filter(cld_company=self.request.user.user_company).\
                             filter(cld_status=1).order_by('-modified_date')[:20]
        context['checklistsdone'] = checklistsdone
        return context


def autocomplete_search_mat(request):
    data = {}
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        manager = request_data['manager']
        if request.user.is_superuser:
            query = Q()
        else:
            query = Q(mat_company=request.user.user_company)
        if manager != '':
            query &= Q(mat_manager_id=manager)
        materials = Material.objects.filter(query).order_by("mat_designation")
        # print(materials)
        data = serializers.serialize('json', materials)
    return HttpResponse(data)


def autocomplete_search_man(request):
    data = {}
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        material = request_data['material']
        if request.user.is_superuser:
            query = Q()
        else:
            query = Q(mgr_company=request.user.user_company)
        if material != '' and material != '0':
            query &= Q(mat_manager__id=material)
        manager = Manager.objects.filter(query).order_by("mgr_name")
        # print(manager)
        data = serializers.serialize('json', manager)
    return HttpResponse(data)


def search_chklst(request):
    data = {}
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        query = Q(cld_status=1)
        if not request.user.is_superuser:
            query &= Q(cld_company=request.user.user_company)
        if 'material' in request_data:
            query &= Q(cld_material_id=request_data['material'])
        if 'manager' in request_data:
            query &= Q(cld_manager_id=request_data['manager'])
        if 'date' in request_data:
            query &= Q(modified_date__icontains=request_data['date'])
        # print(query)
        checklists_done = CheckListDone.objects.filter(query).order_by('-modified_date')[:20]
        # print(checklists_done)
        data = []
        for idx, chklst in enumerate(checklists_done):
            # print(chklst)
            data.append({'key': chklst.cld_key,
                         'valid': chklst.cld_valid,
                         'pdf': chklst.cld_pdf_file.url,
                         'date': str(chklst.modified_date)[:10],
                         'title': chklst.cld_title[:30],
                         })
            try:
                data[idx]['manager'] = chklst.cld_manager.mgr_name
            except AttributeError:
                data[idx]['manager'] = ''
            try:
                data[idx]['material'] = chklst.cld_material.mat_designation
            except AttributeError:
                data[idx]['material'] = ''
            if request.user.is_superuser:
                data[idx]['company'] = chklst.cld_company.company_name
        data = json.dumps(data)
    return HttpResponse(data)


class ChecklistTable(tables.Table):
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#")

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        if args[2]:
            self.base_columns['chk_key'] = tables.columns.LinkColumn('app_checklist:saisie1', args=[A('pk')])
        else:
            self.base_columns['chk_key'] = tables.columns.LinkColumn('app_checklist:saisie3-priv', args=[A('pk')])
        self.base_columns['chk_title'].verbose_name = Translation.get_translation('Wording', language=args[1])
        self.base_columns['chk_key'].verbose_name = Translation.get_translation('Key', language=args[1])
        self.base_columns['chk_company.company_name'].verbose_name = Translation.get_translation('Company',
                                                                                                 language=args[1])
        super(ChecklistTable, self).__init__(*args, **kwargs)

    class Meta:
        model = CheckList
        fields = ('counter', 'chk_key', 'chk_title', 'chk_company.company_name')
        attrs = {'class': 'table table-striped table-hover'}

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1


class ChecklistdoneTable(tables.Table):
    counter = tables.columns.Column(empty_values=(), orderable=False, verbose_name="#")
    col_del = tables.columns.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name="")
                                   

    class Meta:
        model = CheckListDone
        fields = ('counter', 'cld_key', 'cld_title', 'cld_mat', 'cld_man', 'cld_user.username', 'col_del')
        attrs = {'class': 'table table-striped table-hover'}

    def __init__(self, *args, **kwargs):
        self.row_counter = itertools.count()
        if args[2]:
            self.base_columns['cld_key'] = tables.columns.LinkColumn('app_checklist:saisie1', args=[A('pk'),
                                                                                                    ('inprogress')])
        else:
            self.base_columns['cld_key'] = tables.columns.LinkColumn('app_checklist:saisie3-priv', args=[A('pk')])
        self.base_columns['cld_title'].verbose_name = Translation.get_translation('Wording', language=args[1])
        self.base_columns['cld_key'].verbose_name = Translation.get_translation('Key', language=args[1])
        self.base_columns['cld_mat'].verbose_name = Translation.get_translation('Material', language=args[1])
        self.base_columns['cld_man'].verbose_name = Translation.get_translation('Manager', language=args[1])
        self.base_columns['cld_user.username'].verbose_name = Translation.get_translation('User', language=args[1])
        super(ChecklistdoneTable, self).__init__(*args, **kwargs)

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count())
        return next(self.row_counter) + 1

    def render_col_del(self, *args, **kwargs):
        # print(kwargs['record'].cld_key)
        data_dsp = str(kwargs['record'].cld_key) + " - " + str(kwargs['record'].cld_title)
        tooltip = Translation.get_translation("Delete", username=self.request.user)
        var = '<span data-tooltip="' + tooltip + '"  class="trash" data-pk="' + str(kwargs['record']) + '" \
               data-dsp="' + data_dsp + '">\
               <i class="tabicon fas fa-trash-alt" style="color: red; !important"></i></span>'
        return format_html(var)


def new_main_view(request):
    global language
    context = {'title': "Main"}
    if request.method == 'POST':
        return render(request, "app_home/newmain.html", context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        # get Check-lists & Check-lists done
        if request.user.is_superuser:
            checklists = ChecklistTable(CheckList.objects.all(),
                                        request.user.preferred_language.code,
                                        request.user.pro, prefix="1-")
            checklistsinpro = ChecklistdoneTable(CheckListDone.objects.filter(cld_status=3).order_by('-modified_date'),
                                                 request.user.preferred_language.code,
                                                 request.user.pro, prefix="2-")
            checklistsdone = CheckListDone.objects.filter(cld_status=1).order_by('-modified_date')[:20]
        else:
            checklists = ChecklistTable(CheckList.objects.filter(Q(chk_company=request.user.user_company) |
                                                                 Q(chk_company=999999) & Q(chk_enable=True)),
                                        request.user.preferred_language.code,
                                        request.user.pro, prefix="1-")
            checklistsinpro = ChecklistdoneTable(CheckListDone.objects.filter(
                                                 Q(cld_company=request.user.user_company) & \
                                                 Q(cld_status=3)).order_by('-modified_date'),
                                                 request.user.preferred_language.code,
                                                 request.user.pro, prefix="2-")
            checklistsdone = CheckListDone.objects.filter(Q(cld_company=request.user.user_company) & \
                                                          Q(cld_status=1)).order_by('-modified_date')[:20]

        RequestConfig(request, paginate={"per_page": 5}).configure(checklists)
        RequestConfig(request, paginate={"per_page": 5}).configure(checklistsinpro)

        context['checklists'] = checklists
        context['checklistsdone'] = checklistsdone
        context['checklistsinpro'] = checklistsinpro
        return render(request, "app_home/newmain.html", context=context)
