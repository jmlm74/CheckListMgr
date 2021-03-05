from django.contrib.auth.decorators import login_required
from django.urls import path

from app_create_chklst import views as accv
from app_create_chklst import chklst_views as accclv
from app_create_chklst import heading_views as acchv
from app_create_chklst import line_views as acclv
from app_create_chklst import category_views as acccv

app_name = 'app_create_chklst'
urlpatterns = [
    # Main page for Cheklists
    path('mainchklst/', login_required(accclv.MainChkLstView.as_view()), name='chk-main'),

    # categories and lines tables
    path('catlinemgmt/', login_required(accv.CatandLineMgmtView), name='catlineMgmt'),

    # categories
    path('catcreate/', login_required(acccv.CategoryCreateView.as_view()), name='chk-catcreate'),
    path('catdisplay/<int:pk>', login_required(acccv.CategoryDisplayView.as_view()), name='chk-catdisplay'),
    path('catupdate/<int:pk>', login_required(acccv.CategoryUpdateView.as_view()), name='chk-catupdate'),
    path('catdelete/<int:pk>', login_required(acccv.CategoryDeleteView.as_view()), name='chk-catdelete'),
    path('catmgmt/', login_required(acccv.category_mgmt_view), name='chk-catmgmt'),

    # lines
    path('linecreate/', login_required(acclv.LineCreateView.as_view()), name='chk-linecreate'),
    path('linedisplay/<int:pk>', login_required(acclv.LineDisplayView.as_view()), name='chk-linedisplay'),
    path('lineupdate/<int:pk>', login_required(acclv.LineUpdateView.as_view()), name='chk-lineupdate'),
    path('linedelete/<int:pk>', login_required(acclv.LineDeleteView.as_view()), name='chk-linedelete'),
    # path('linemgmt/', login_required(accv.LineMgmtView.as_view()), name='chk-linemgmt'),
    path('linemgmt/', login_required(acclv.line_mgmt_view), name='chk-linemgmt'),

    # ckeck-lists
    path('chkcreate/', login_required(accclv.ChkLstCreateView.as_view()), name='chk-chklstcreate'),
    path('chklstdelete/<int:pk>', login_required(accclv.ChklstDeleteView.as_view()), name='chk-chkdelete'),
    path('chklstdisplay/<int:pk>', login_required(accclv.ChklstDisplayView.as_view()), name='chk-chkdisplay'),
    path('chklstupdate/<int:pk>', login_required(accclv.ChkLstUpdateView.as_view()), name='chk-chkupdate'),
    path('chklstcopy/<int:pk>', login_required(accclv.ChkLstCopyView.as_view()), name='chk-chkcopy'),
    path('chklstcopy/', login_required(accclv.ChkLstCopyView.as_view()), name='chk-chkcopy'),

    # Ajax create chklst
    path('create_chklst/', login_required(accclv.create_chklst), name='create_chklst'),

    # Headings
    path('headingsmgmt/', login_required(acchv.head_mgmt_view), name='chk-headmgmt'),
    path('headingcreate/', login_required(acchv.HeadingCreateView.as_view()), name='chk-headingcreate'),
    path('headingdelete/<int:pk>', login_required(acchv.HeadingDeleteView.as_view()), name='chk-headingdelete'),
    path('headingupdate/<int:pk>', login_required(acchv.HeadingUpdateView.as_view()), name='chk-headingupdate'),
    path('headingdisplay/<int:pk>', login_required(acchv.HeadingDisplayView.as_view()), name='chk-headingdisplay'),

]
