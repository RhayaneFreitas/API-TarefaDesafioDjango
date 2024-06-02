from api.apps.task.views import user
from api.apps.task.views import user as taskviewsets
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

#####
from rest_framework import routers
from django.urls import(
    path,
    include
)
from api.apps.task.views.user import (
    ExportData,
    ExportFilters,
    TaskReportFilters
    
)

from rest_framework.routers import DefaultRouter
route = routers.DefaultRouter()

route.register(r'tasks-list', taskviewsets.TaskViewsSet, basename="Task")

urlpatterns = [
    path(
        'token/',
        TokenObtainPairView.as_view(
        )
    ),
    path(
        'token/refresh/', 
        TokenRefreshView.as_view(
            
        )
    ),
    path(
        'task-view/',
        user.TaskView.as_view(
            
        )
    ),
    path('',
         include(route.urls)
    ),
    path('export/<slug:slug>/',
         user.ExportFilters.as_view(
             
         ),
         name='export_filters'
    ),
    path('export_data/',
         ExportData.as_view(),
         name='exportdata'
    ),
    path('export_report/<str:report_type>/',
         TaskReportFilters.as_view(),
         name='task-report' 
    ),
    
]


"""Antes das Melhorias:

1 - Método de Escrita com :
path('export_data/<int:pk>/<slug:slug>/',ExportData.as_view(), name='exportdata') 

2 - Melhoria no Método de Escrita e Junção Txt/Json em uma única Classe:

    # path('export/json/',
    #      user.ExportJson.as_view(
             
    #      ),
    #      name='export_tasks'
    # ),
    # path('export/txt/',
    #      user.ExportTxt.as_view(
             
    #      ),
    #      name='task-export-txt'
    # ),
    # path('<int:pk>/', user.TaskView.as_view(
        
    #     ),
    # ),




"""
