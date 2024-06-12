from api.apps.task.views import user
from api.apps.task.views import user as taskviewsets
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from rest_framework import routers
from django.urls import(
    path,
    include
)
from api.apps.task.views.user import (
    ExportData,
    TasksCreatedFinishedByUserView,
    ActivitiesByResponsibleView,
    LateTasksView,
    UserFinishedOwnTasksView,
    UserCreatedAndFinishedTasksView
    
)

from rest_framework.routers import DefaultRouter
route = routers.DefaultRouter()

route.register(r'tasks', taskviewsets.TaskViewsSet, basename="task") # Vizualização Web

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
            
        ),
        name='task-view'
    ),
    path('',
         include(route.urls)
    ),
    path(
        'export_data/',
         ExportData.as_view(),
         name='exportdata'
    ),
    path('export/',
         include(
             [
                 path(
                    'user-finished-own-tasks/',
                    UserFinishedOwnTasksView.as_view(),
                     name='export_user_tasks'
                 ),
                path(
                    'user-created-and-finished-tasks/',
                    UserCreatedAndFinishedTasksView.as_view(),
                    name='user-created-and-finished-tasks'
                ),
                path(
                    'late-tasks/', 
                    LateTasksView.as_view(),
                    name='late-tasks'
                ),
                path(
                    'activities-by-responsible/',
                    ActivitiesByResponsibleView.as_view(),
                    name='activities-by-responsible'
                ),
                path(
                    'tasks-created-finished-by-user/',
                    TasksCreatedFinishedByUserView.as_view(),
                    name='tasks-created-finished-by-user'
                ),
                    
             ]
         )
        
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
        path('export/<slug:slug>/',
         user.ExportFilters.as_view(
             
         ),
         name='export_filters'
    ),

    # path('export-report/<str:report_type>/',
    #      TaskReportFilters.as_view(),
    #      name='task_report_filters' 
    # ),
    
    # path('user-finished-own-tasks/',
    #      UserFinishedOwnTasksView.as_view(),
    #      name='user-finished-own-tasks'
    # ),
        # path(
    #     'export-tasks-created-finished-by-user/',
    #      TasksCreatedFinishedByUserView.as_view(),
    #      name='tasks-created-finished-by-user'
    # ),
    # path(
    #     'export-activities-by-responsible/',
    #      ActivitiesByResponsibleView.as_view(),
    #      name='activities-by-responsible'
    # ),
    # path(
    #     'export-late-tasks/', 
    #      LateTasksView.as_view(),
    #      name='late-tasks'
    # ),
    # path(
    #     'export-user-created-and-finished-tasks/',
    #      UserCreatedAndFinishedTasksView.as_view(),
    #      name='user-created-and-finished-tasks'
    # ),
    # path(
    #     'export-user-finished-own-tasks/', 
    #      UserFinishedOwnTasksView.as_view(),
    #      name='export_user_tasks'
    # ),


"""
