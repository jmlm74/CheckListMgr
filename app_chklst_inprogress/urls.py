from django.contrib.auth.decorators import login_required
from django.urls import path


from app_chklst_inprogress import views as acv

app_name = 'app_chklst_inprogress'
urlpatterns = [
    # Main page for Cheklists
    # path('mainchklst/', login_required(accclv.MainChkLstView.as_view()), name='chk-main'),

]
