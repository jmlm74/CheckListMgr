import json
from datetime import date, datetime

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from app_checklist.forms import ChekListInput4Form
from app_checklist.models import CheckListPhoto, CheckListDone
from app_create_chklst.models import CheckList
from app_input_chklst.models import Material, Manager


class ChekListInput4(View):
    """
    view for input manager of a checklist
    """
    context = {'title': 'LastPart'}
    template_name = "app_checklist/checklist_finale.html"
    form = ChekListInput4Form
    context_object_name = 'Checklist'

    def get(self, request):
        self.context['checklist'] = ""
        self.context['form'] = self.form()
        self.context['newchecklist_id'] = request.session['newchecklist_id']
        # 1st load
        if 'chksave' not in request.session or request.session['chksave'] == 0:
            request.session['chksave'] = {}
            # request.session['chksave'] = 0
            request.session['chksave']['cld_status'] = 0
            self.context['form'] = self.form
        else:
            newchecklist = CheckListDone.objects.get(pk=request.session['newchecklist_id'])
            fotos = newchecklist.pho_chklst.all()
            fotosave = []
            for foto in fotos:
                fotosave.append(str(foto.pho_file))
                # print(foto.pho_file)
            # date format not jsonified --> None becomes 'None' !
            if request.session['chksave']['cld_date_valid'] == 'None':
                cld_date_valid = None
            else:
                cld_date_valid = request.session['chksave']['cld_date_valid']
            self.context['form'] = self.form(initial={'cld_key': request.session['chksave']['cld_key'],
                                                      'cld_valid': request.session['chksave']['cld_valid'],
                                                      'cld_remarks': request.session['chksave']['cld_remarks'],
                                                      'cld_date_valid': cld_date_valid,
                                                      'cld_email': request.session['chksave']['cld_email'],
                                                      'cld_fotosave': fotosave})
        return render(request, self.template_name, context=self.context)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            # valid --> save the form in session
            if 'cld_status' in request.session['chksave']:
                cld_status = request.session['chksave']['cld_status']
            else:
                cld_status = 0
            request.session['chksave'] = {}
            request.session['chksave']['cld_key'] = form.cleaned_data['cld_key']
            request.session['chksave']['cld_date_valid'] = form.cleaned_data['cld_date_valid']
            request.session['chksave']['cld_valid'] = form.cleaned_data['cld_valid']
            request.session['chksave']['cld_remarks'] = form.cleaned_data['cld_remarks']
            request.session['chksave']['cld_status'] = cld_status
            request.session['chksave']['cld_email'] = form.cleaned_data['cld_email']
            new_checklist = before_preview(request)
            # the request id jsonified but date format is NOT jsonified
            request.session['chksave']['cld_date_valid'] = str(form.cleaned_data['cld_date_valid'])
            if 'previous' in request.POST:
                return redirect('app_checklist:saisie3')
            elif 'keep' in request.POST:
                new_checklist.cld_status = 3
                new_checklist.save()
                return redirect('app_checklist:pdf', save='3')
            else:
                new_checklist.cld_status = 1
                new_checklist.save()
                return redirect('app_checklist:pdf', save='1')
        else:
            messages.error(request, "Error - Fill the fields please")

            return render(request, 'app_checklist/checklist_finale.html', {'form': form,
                                                                           'title': self.context['title']})
        return redirect('app_home:main')


# @csrf_exempt
def before_preview(request):
    """
    function to save datas in database before preview PDF and previous button.
    Also called if ANY elt in the form page is modified (cf script.js)
    The save should be the same but if preview the POST request datas are not the same.
    If ajax --> get data in the "request post json data" and treat it
    If Previous button : Get the data in the request POST.
    Generate a ChecklistDone model to get it in the pdfpreview (no context data because not html render)
    args : request (POST but with data or json depending on the request)
    return : json response if ajax or nothing (called by the post-view)
    """
    newchecklist = CheckListDone.objects.get(pk=request.session['newchecklist_id'])
    checklist = CheckList.objects.get(pk=request.session['checklist_id'])
    newchecklist.cld_status = request.session['chksave']['cld_status']

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        is_ajax = True
        # data = {'data': 'ERREUR'}
        request_data = json.loads(request.read().decode('utf-8'))
        # print(request.headers)
        # print(request_data)
        cld_key = request_data['cld_key']
        cld_valid = request_data['cld_valid']
        if cld_valid:
            cld_valid = 'on'
        cld_remarks = request_data['cld_remarks']
        cld_date_valid = request_data['cld_date_valid']
        cld_email = request_data['cld_email']
        if len(cld_date_valid) == 0:
            cld_date_valid = None
    else:
        is_ajax = False
        cld_key = request.POST['cld_key']
        cld_valid = request.POST.get('cld_valid', 'off')
        cld_remarks = request.POST['cld_remarks']
        cld_email = request.POST['cld_email']
        if request.session['chksave']['cld_date_valid'] == 'None':
            cld_date_valid = None
        else:
            cld_date_valid = request.session['chksave']['cld_date_valid']

    if len(cld_key) == 0:
        newchecklist.cld_key = str(datetime.now().timestamp())[:15]
    else:
        newchecklist.cld_key = cld_key
    newchecklist.cld_remarks = cld_remarks
    if cld_valid == 'on':
        newchecklist.cld_valid = True
    else:
        newchecklist.cld_valid = False


    newchecklist.cld_user = request.user
    newchecklist.cld_company = request.user.user_company
    newchecklist.cld_checklist = checklist
    newchecklist.cld_title = checklist.chk_title
    newchecklist.cld_date_valid = cld_date_valid
    newchecklist.cld_remarks = cld_remarks
    newchecklist.cld_email = cld_email
    newchecklist.cld_save = request.session['chklst']['save']
    newchecklist.cld_remsave = request.session['chklst']['remsave']
    if request.session['mat']['id'] != '0':
        newchecklist.cld_material = Material.objects.get(pk=request.session['mat']['id'])
        newchecklist.cld_mat = newchecklist.cld_material.mat_designation
    if request.session['mgr']['id'] != '0':
        newchecklist.cld_manager = Manager.objects.get(pk=request.session['mgr']['id'])
        newchecklist.cld_man = newchecklist.cld_manager.mgr_name
    newchecklist.save()
    if is_ajax:
        data = {'data': 'OK'}
        return JsonResponse(data)
    return newchecklist


@csrf_exempt
def file_upload_view(request):
    # print(request.FILES)
    data = {'data': 'ERREUR'}
    if request.method == 'POST':
        # print(request.POST)
        my_file = request.FILES.get('file')
        newchecklist_id = request.POST.get('newchecklist_id', None)
        caption = request.POST.get('caption', None)
        data = {}
        if newchecklist_id is not None:
            newchecklist = CheckListDone.objects.get(pk=newchecklist_id)
            CheckListPhoto.objects.create(pho_file=my_file,
                                          pho_caption=caption,
                                          pho_chklst_done=newchecklist)
            data['data'] = 'OK'
    return JsonResponse(data)


@csrf_exempt
def file_remove_view(request):
    data = {'data': 'ERREUR'}
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        # print(request_data)
        filename = request_data['filename'].split('.')[0]
        checklist_id = request_data['checklist_id']
        today = date.today()
        newchecklist = CheckListDone.objects.get(pk=checklist_id)
        foto = newchecklist.pho_chklst.filter(pho_file__contains=filename).\
            filter(created_date__year=today.year, created_date__month=today.month, created_date__day=today.day)
        foto[0].delete()
        data = {'data': 'OK'}
    return JsonResponse(data)
