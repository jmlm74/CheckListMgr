from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render

from app_create_chklst.models import (Category,
                                      Line)


def CatandLineMgmtView(request):
    """
    display page with 2 tables : Categories & lines
    Context has 2 querysets (lines and categories) and parameters is for the 2 paginators
    if POST --> render the page
    if GET -->
        --> find if an error message and find for what (line or cat)
        --> get the querysets
        --> paginate
        --> render the page
    The whole CRUD for cat and lines are in the table.
    :param request:
    :return: render
    """
    context = {'title': "app_create_chklst_catlinemgmt_title"}
    if request.method == 'POST':
        return render(request, 'app_create_chklst/catandlinemgmt.html', context=context)
    if request.method == 'GET':
        list(messages.get_messages(request))
        if error := request.GET.get('error', None, ):
            if error[0:4] == 'Line':
                context['line_error'] = error
            else:
                context['error'] = error
        if message := request.GET.get('message', None, ):
            if message[0:4] == 'Line':
                context['line_message'] = message
            else:
                context['message'] = message
        # get Categories & lines
        if request.user.is_superuser:
            categories = Category.objects.all()
            lines = Line.objects.all()
        else:
            categories = Category.objects.filter(Q(cat_company=request.user.user_company))
            lines = Line.objects.filter(Q(line_company=request.user.user_company))
        # Cat paginator
        cat_page = request.GET.get('catpage', 1, )
        cat_paginator = Paginator(categories, 5)
        try:
            cat_users = cat_paginator.page(cat_page)
        except PageNotAnInteger:
            cat_users = cat_paginator.page(1)
        except EmptyPage:
            cat_users = cat_paginator.page(cat_paginator.num_pages)

        # Lines paginator

        line_page = request.GET.get('linepage', 1, )
        line_paginator = Paginator(lines, 5)
        try:
            line_users = line_paginator.page(line_page)
        except PageNotAnInteger:
            line_users = line_paginator.page(1)
        except EmptyPage:
            line_users = line_paginator.page(line_paginator.num_pages)

        context['categories'] = categories
        context['cat_users'] = cat_users
        context['line_users'] = line_users
        context['cur_page_cat'] = cat_page
        context['cur_page_line'] = line_page
        return render(request, 'app_create_chklst/catandlinemgmt.html', context=context)


