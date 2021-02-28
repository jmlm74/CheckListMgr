import json
from django.db.models import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app_utilities.models import Translation
from app_user.models import Address
from django.core import serializers


@csrf_exempt
def get_message(request):
    """
    Ajax function
    args - Request --> Get data in, json format : Message to get the translation
    returns : The translation in user language or UK if no user connected in json format
    """
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        msg = request_data['msg']
        try:
            language = request.session['language']
        except KeyError:
            language = "UK"
        text_to_display = Translation.get_translation(msg, language=language)
        data = {'msg': text_to_display, 'data': 'OK'}
    return JsonResponse(data)


@csrf_exempt
def get_address(request):
    """
        Ajax function
        args - Request --> Get data in, json format : id for the address to return
        returns : The address found in json format or ERREUR
        """
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        id_address = request_data['id']
        address = Address.objects.filter(pk=int(id_address))
        if not address:
            data = {'data': 'Error'}
        else:
            address = serializers.serialize("json", address)
            data = {'address': address, 'data': 'OK'}
    return JsonResponse(data)


def render_col_del_generic(pk, user):
    """
    render col (eye-edit-trash) for tables2
    """
    tooltip = Translation.get_translation("Display", username=user)
    var = '<span data-tooltip="' + tooltip + '" class="Display-class" id="' + pk + 'D">' \
          '<i class="tabicon fas fa-eye mr-2" style="color: forestgreen; !important"></i>' \
          '</span>'
    tooltip = Translation.get_translation("Update", username=user)
    var += '<span data-tooltip="' + tooltip + '" class="Update-class" id="' + pk + 'U">' \
           '<i class="tabicon fas fa-edit mr-2" style="color: dodgerblue;"></i>' \
           '</span>'
    tooltip = Translation.get_translation("Delete", username=user)
    var += '<span data-tooltip="' + tooltip + '" class="Remove-class" id="' + pk + 'R">' \
           '<i class="tabicon fas fa-trash-alt" style="color: red;"></i>' \
           '</span>'
    return var


def render_enable_generic(value):
    if value:
        var = '<i class="fas fa-check" style="color: green" > </i>'
    else:
        var = '<i class="fas fa-times" style="color: red" > </i>'
    return var
