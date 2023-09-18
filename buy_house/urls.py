from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('del_obj', views.ObjCompare.find_del_obj, name = 'del_obj'),
    path('new_obj', views.ObjCompare.find_new_obj, name = 'new_obj'),
    path('obj_update', views.ObjCompare.price_update, name = 'obj_update'),
    path('find_addr', views.ObjCompare.get_noaddr_keys, name = 'find_addr'),
    path('addr_update', views.ObjCompare.addr_update, name = 'addr_update'),
    path('find_group', views.ObjCompare.find_group, name = 'find_group'),
    path('createtasks', views.spider_form_view, name = 'createtasks'),
]