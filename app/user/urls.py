from django.urls import path
from erp.views import *
from user.views import *

urlpatterns = [
    path('list/', UserListView.as_view(), name='userlist'),
    path('create/',UserCreateView.as_view(), name='usercreate'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='userdelete'),
    path('test/', TestView.as_view(), name='testview')
]