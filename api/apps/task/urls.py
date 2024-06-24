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
    CreateUserView,
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
        'create/',
        CreateUserView.as_view(
            
        ),
        name='create-user'
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

