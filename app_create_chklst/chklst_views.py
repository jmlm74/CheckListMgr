import json

from sortable_listview import SortableListView
from bootstrap_modal_forms.generic import BSModalDeleteView, BSModalReadView, BSModalFormView

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import View

from app_create_chklst.forms import CheckListCreateForm, CheckListCopyForm
from app_create_chklst.models import (Category,
                                      CheckListLine,
                                      CheckListCategory,
                                      CheckList,
                                      Line)
from app_user.models import Company


class ChklstDeleteView(BSModalDeleteView):
    """
    Delete checklist
    --> Modal delete view
    """
    template_name = 'app_create_chklst/dialogboxes/deletechklst.html'
    model = CheckList
    success_message = 'DeletechklstOK'
    success_url = reverse_lazy('app_create_chklst:chk-main')


class ChklstDisplayView(BSModalReadView):
    """
    display checklist
    --> Modal display view
    """
    context = {'title': 'Chklistdisplay'}
    template_name = 'app_create_chklst/dialogboxes/displaychklst.html'

    def get(self, request, **kwargs):
        """
        --> get the datas for the display view
        :param request:
        :param kwargs: --> pk --> view id
        :return: template modal
        """
        pk = kwargs['pk']
        checklist = CheckList.objects.get(pk=pk)
        details = checklist.chklst_detail()
        self.context['details'] = details
        self.context['checklist'] = checklist
        return render(request, self.template_name, context=self.context)


# @csrf_exempt
@transaction.atomic
def create_chklst(request):
    """
    Create checklist --> Ajax request
    if POST (GET method bot treated)
        --> call create_chklst function --> reusable
        --> get the data from the request (JSON format)
        --> if Checklist already exists --> update - otherwise --> insert
        --> lines (blank array if no lines) --> cat & lines
            --> delete all the lines & cat for the specified checklist (0 if creation but doesn't matter) --> many
                to many through relationship
            --> the catline is : lin-45 or cat-33 --> 3 1st car --> line or cat then the id
            --> insert into the many to many relationship the line or cat with the id and th position (loop counter)
        --> return the rigth message if create or update
    :param request: all the checklist + lines & categories
    :return: OK or Erreur (just OK is verified !)
    """
    if request.method == 'POST':
        data = {'data': 'ERROR'}
        request_data = json.loads(request.read().decode('utf-8'))
        data = create_chklst_fct(request, request_data)
    return JsonResponse(data)


@transaction.atomic
def create_chklst_fct(request, request_data):
    """
    cf create_chklst
    """
    chk_key = request_data['chk_key']
    chk_title = request_data['chk_title']
    chk_enable = request_data['chk_enable']
    if 'chk_company' in request_data:
        chk_company = Company.objects.get(pk=request_data['chk_company'])
    else:
        chk_company = request.user.user_company

    lines = request_data['lines']
    position = 0
    if CheckList.objects.filter(Q(chk_key=chk_key) & Q(chk_company=chk_company)).exists():
        if request_data['action'] == 'create':
            data = {'data': 'Erreur'}
            messages.error(request, "Duplchkkey")
            return data
        CheckList.objects.filter(Q(chk_key=chk_key) & Q(chk_company=chk_company))\
            .update(chk_title=chk_title,
                    chk_enable=chk_enable,
                    chk_company=chk_company,
                    chk_user_id=request.user.id)
    else:
        CheckList.objects.create(chk_key=chk_key,
                                 chk_title=chk_title,
                                 chk_enable=chk_enable,
                                 chk_company=chk_company,
                                 chk_user_id=request.user.id)
    new_checklist = CheckList.objects.get(Q(chk_key=chk_key) & Q(chk_company=chk_company))
    CheckListLine.objects.filter(chk_line_checklist=new_checklist).delete()
    CheckListCategory.objects.filter(chk_cat_checklist=new_checklist).delete()
    for line in lines:
        cat_line = line[0:3]
        catline_id = line[4:]
        print(f"{line} - {cat_line} - {catline_id}")
        if cat_line == "cat":
            category = Category.objects.get(pk=int(catline_id))
            chkcat, created = CheckListCategory.objects.update_or_create(chk_cat_position=position,
                                                                         chk_cat_category=category,
                                                                         chk_cat_checklist=new_checklist)
            chkcat.save()
        else:
            line = Line.objects.get(pk=int(catline_id))
            chkline, created = CheckListLine.objects.update_or_create(chk_line_position=position,
                                                                      chk_line_line=line,
                                                                      chk_line_checklist=new_checklist)
            chkline.save()
        position += 1
    data = {'data': 'OK'}
    try:
        if request_data['action'] == 'create':
            messages.success(request, "CreatechklstOK")
        elif request_data['action'] == 'update':
            messages.success(request, "UpdatechklstOK")
        else:
            messages.success(request, "CopychklstOK")
    except KeyError:
        pass
    return data

# noinspection PyTypeChecker
class ChkLstCreateView(View):
    """
    Checklist Create View
    Prepare the view : 3 cols with the lines and categories of the company (the last is empty - Checklist)
    put the results of the 2 queries in the context data and render the form
    All the create is treated by JS and Ajax function below.
    """
    context = {'title': 'Chklstcreate'}
    form = CheckListCreateForm
    success_url = reverse_lazy('app_create_chklst:chk-main')

    def get(self, request):
        if request.user.is_superuser:
            categories = Category.objects.all().order_by('cat_company')
            lines = Line.objects.all().order_by('line_company')
        else:
            categories = Category.objects.filter(Q(cat_company=request.user.user_company) & Q(cat_enable=True))\
                .order_by('cat_key')
            lines = Line.objects.filter(Q(line_company=request.user.user_company) & Q(line_enable=True))\
                .order_by('line_key')
        self.context['categories'] = categories
        self.context['lines'] = lines
        self.context['form'] = self.form
        return render(request, 'app_create_chklst/createchklst.html', context=self.context)

    def post(self, request):
        return self.success_url


# noinspection PyTypeChecker
class ChkLstUpdateView(View):
    """
        Checklist Create View
        Prepare the view : 3 cols with the lines and categories of the company and the checklist's lines & cats
        put the results of the 3 queries in the context data and render the form
         - The lines and the cats which are not in the checklist
         - The line and cats in the checklist well ordered
        All the create is treated by JS and Ajax function below.
        """
    context = {'title': 'Chklstupdate'}
    form = CheckListCreateForm
    success_url = reverse_lazy('app_create_chklst:chk-main')

    def get(self, request, pk):
        if request.user.is_superuser:
            categories = Category.objects.all().order_by('cat_company')
            lines = Line.objects.all().order_by('line_company')
        else:
            categories = Category.objects.filter(Q(cat_company=request.user.user_company) & Q(cat_enable=True))\
                .order_by('cat_key')
            lines = Line.objects.filter(Q(line_company=request.user.user_company) & Q(line_enable=True))\
                .order_by('line_key')
        self.context['categories'] = categories
        self.context['lines'] = lines
        checklist = CheckList.objects.get(pk=pk)
        details = checklist.chklst_detail()
        self.context['details'] = details
        self.context['checklist'] = checklist
        self.context['form'] = self.form(initial={'chk_key': checklist.chk_key,
                                                  'chk_title': checklist.chk_title,
                                                  'chk_enable': checklist.chk_enable,
                                                  'chk_company': checklist.chk_company, })
        return render(request, 'app_create_chklst/updatechklst.html', context=self.context)

    def post(self, request):
        return self.success_url


class MainChkLstView(SortableListView):
    """
    Main view --> Sortable list view
    """
    context = {'title': 'Checklists'}
    template_name = "app_create_chklst/mainchklst.html"
    context_object_name = "checklists"
    allowed_sort_fields = {"chk_key": {'default_direction': '', 'verbose_name': 'Key'},
                           "chk_title": {'default_direction': '', 'verbose_name': 'Wording'},
                           "chk_enable": {'default_direction': '', 'verbose_name': 'Enable'}, }
    default_sort_field = 'chk_key'  # mandatory
    paginate_by = 5

    def get_queryset(self):
        order = self.request.GET.get('sort', 'chk_key')

        if self.request.user.is_superuser:
            return CheckList.objects.all().order_by(order)
        else:
            return CheckList.objects.filter(chk_company=self.request.user.user_company_id)\
                .order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', 'chk_key')
        context['title'] = 'Checklists'
        return context


class ChkLstCopyView(BSModalFormView):
    """
    Checklist copy view BS Modal Form --> generic view
    - get_context_data
        --> to get the source checklist and pass in context to display old fields in form inputs
    - POST
        --> valid the form -−> not valid --> exit with message (redirect to main)
            --> valid --> get the new key & title + get all the details of the source
                      --> call the create_checklist with all the datas
                      --> redirect to main
    """
    context = {'title': 'Chklistcopy'}
    template_name = 'app_create_chklst/dialogboxes/copychklst.html'
    form_class = CheckListCopyForm
    success_url = reverse_lazy('app_create_chklst:chk-main')
    success_message = 'LineCreateOK'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        old_id = int(self.kwargs['pk'])
        old_checklist = CheckList.objects.get(pk=old_id)
        context['checklist'] = old_checklist
        return context

    def post(self, request, *args, **kwargs):
        print('POST')
        copy_form = CheckListCopyForm(request.POST)
        if 'cancel-btn' in request.POST:
            print("Cancel")
            messages.error(request, "Canceled")
            return redirect(self.success_url)
        if copy_form.is_valid():
            old_id = kwargs['pk']
            old_checklist = CheckList.objects.get(pk=old_id)
            details = old_checklist.chklst_detail()
            lines = []
            for detail in details:
                line = f"{detail['line_cat'][0:3]}-{detail['id']}"
                lines.append(line)
            data = {'action': 'copy',
                    'chk_key': copy_form.cleaned_data['chk_newkey'],
                    'chk_title': copy_form.cleaned_data['chk_newtitle'],
                    'chk_enable': old_checklist.chk_enable,
                    'lines': lines}
            new_data = create_chklst_fct(request, data)
        else:
            messages.error(request, "Duplchkkey")
        return redirect(self.success_url)
