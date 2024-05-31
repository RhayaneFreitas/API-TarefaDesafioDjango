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
    path('export/json/',
         user.ExportJson.as_view(
             
         ),
         name='export_tasks'
    ),
    path('export/txt/',
         user.ExportTxt.as_view(
             
         ),
         name='task-export-txt'
    ),
    path('<int:pk>/', user.TaskView.as_view(
        
        ),
    ),
    path('export/filters/',
         user.ExportFilters.as_view(
             
         ),
         name='export_filters'
    ),
]

# path('export_data/<int:pk>/<slug:slug>/',ExportData.as_view(), name='exportdata') > Transformaria em 1 só.