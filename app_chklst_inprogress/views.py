from django.shortcuts import render
from django.db.models import Q

from sortable_listview import SortableListView

from app_checklist.models import CheckListDone


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
            return CheckListDone.objects.all().order_by(order)
        else:
            return CheckListDone.objects.filter(Q(cld_company=self.request.user.user_company_id) & \
                                                Q(cld_status=3)).order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', 'chk_key')
        context['title'] = 'Checklists'
        return context

