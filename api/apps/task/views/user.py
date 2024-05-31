from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import json
from api.apps.task.serializers.user import (
    TasksSerializer,
    TaskResponsibleSerializer,
    )
from api.apps.task.serializers import user
from api.apps.task.models import (
    TaskProfile,
    
    )
from api.apps.task.models import user
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from django.contrib.auth.models import (
    User as AuthUser,
)
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend

# from api.apps.task.serializers import TasksSerializer
from rest_framework import (
    permissions,
    status,
    viewsets,
    filters,
    )

from django.db.models import Count
from django.db.models import Q

class TaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        
        tasks = TaskProfile.objects.all()
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TasksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            task = TaskProfile.objects.get(pk=pk)
        except TaskProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = TasksSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = TaskProfile.objects.get(pk=pk)
        except TaskProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ExportJson(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request):
        tasks = TaskProfile.objects.all()
        serializer = TasksSerializer(tasks, many=True)
        content = JSONRenderer().render(serializer.data)
        # print(content)
        # content_filters = []
        # for item in content:
        #     if item['']
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="tasks.json"'
        return response

# class ExportFilters(APIView):
#     renderer_classes = [JSONRenderer]
    
#     def get(self, request):
#         responsibles = user.TaskResponsible.objects.all()
#         # test = user.TaskProfile.objects.filter
#         serializer_responsibles = TaskResponsibleSerializer(responsibles, many=True)
#         content_responsibles = JSONRenderer().render(serializer_responsibles.data)
        
#         tasks = user.TaskProfile.objects.all()
#         serializer_tasks = TasksSerializer(tasks, many=True)
#         content_tasks = JSONRenderer().render(serializer_tasks.data)
#         content = self.filters(content_responsibles, content_tasks)
#         response = HttpResponse(content, content_type='application/json')
#         response['Content-Disposition'] = 'attachment; filename="filters.json"'
#         return response
    
#     def filters(self,content_responsibles, content_tasks):
#         num_responsibles = user.TaskResponsible.objects.count()
#         num_tasks = user.TaskProfile.objects.count()
#         num_users = AuthUser.objects.count()
#         print(num_users)
#         # for responsible in content_responsibles:
#         content = []
#         for i in range(num_users):
#             a = user.TaskProfile.objects.filter(created_by=i).count()
#             b = user.TaskProfile.objects.filter(finished_by=i).count()
#             dict = {"TasksCreatedPerUser": a,
#                     "TasksFinishedPerUser": b}
#             content.append(dict)
#         repr_content = repr(content)
#         bytes_content = repr_content.encode('utf-8')

#         return bytes_content

class ExportFilters(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request):

        responsibles = user.TaskResponsible.objects.all()
        serializer_responsibles = TaskResponsibleSerializer(responsibles, many=True)

        tasks = TaskProfile.objects.all()
        serializer_tasks = TasksSerializer(tasks, many=True)
        
        content = self.filters()
        
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="filters.json"'
        return response
    
    def filters(self):
        num_responsibles = user.TaskResponsible.objects.count()
        num_tasks = TaskProfile.objects.count()
        num_users = AuthUser.objects.count()
        
        content = []
        for user_id in range(1, num_users + 1):
            tasks_created = TaskProfile.objects.filter(created_by=user_id).count()
            tasks_finished = TaskProfile.objects.filter(finished_by=user_id).count()
            dict_content = {
                "TasksCreatedPerUser": tasks_created,
                "TasksFinishedPerUser": tasks_finished
            }
            content.append(dict_content)
        
        json_content = JSONRenderer().render(content)
        return json_content

class ExportTxt(APIView):
###################################################################
    def get(self, request):
        tasks = TaskProfile.objects.all()
        content =''
        for task in tasks:
            serializer_task = TasksSerializer(task).data
            content += (
                f'Titulo: {serializer_task["title"]}, '
                f'Descricao: {serializer_task["description"]}, '
                f'Data de Lançamento: {serializer_task["release"]}, '
                f'Finalizada: {serializer_task["completed"]}, '
                f'Finalizada Em: {serializer_task["finished_in"]}, '
                f'Finalizada Por: {serializer_task["finished_by"]}, '
                f'Criada Em: {serializer_task["created_in"]}, '
                f'Atualizada: {serializer_task["updated"]}, '
                f'Responsavel: {serializer_task["responsible"]}, '
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="tasks.txt"'
        return response




# class ExportJson(APIView):
#     renderer_classes = [JSONRenderer]
    
#     def get(self, request):
#         tasks = TaskProfile.objects.all()
#         serializer = TasksSerializer(tasks, many=True)
#         content = JSONRenderer().render(serializer.data) # Converte os dados serializados em json
#         response = HttpResponse(content, content_type='application/json')
#         response['Content-Disposition'] = 'attachment; filename="tasks.json"' # Baixa o arquivo
#         return response
    
# class ExportTxt(APIView):
# ###################################################################
#     def get(self, request):
#         tasks = TaskProfile.objects.all()
#         content =''

#         for task in tasks:
#             serializer_task = TasksSerializer(task).data
#             content += (
#                 f'Titulo: {serializer_task["title"]}, '
#                 f'Descricao: {serializer_task["description"]}, '
#                 f'Data de Lançamento: {serializer_task["release"]}, '
#                 f'Finalizada: {serializer_task["completed"]}, '
#                 f'Finalizada Em: {serializer_task["finished_in"]}, '
#                 f'Finalizada Por: {serializer_task["finished_by"]}, '
#                 f'Criada Em: {serializer_task["created_in"]}, '
#                 f'Atualizada: {serializer_task["updated"]}, '
#                 f'Responsavel: {serializer_task["responsible"]}, '
#             )
#         response = HttpResponse(content, content_type='text/plain')
#         response['Content-Disposition'] = 'attachment; filename="tasks.txt"'
#         return response

class TaskViewsSet(viewsets.ModelViewSet):
    serializer_class = TasksSerializer
    queryset = user.TaskProfile.objects.all()
    # filter_backends = (filters.SearchFilter,) simples
    # search_fields = ('title', 'release')
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['created_in', 'finished_in']
    


    

