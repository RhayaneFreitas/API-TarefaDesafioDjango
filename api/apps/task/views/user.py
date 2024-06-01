from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import json
from datetime import (
    datetime,
    timedelta
)
from api.apps.task.serializers.user import (
    TasksSerializer,
    TaskResponsibleSerializer,
    )
from api.apps.task.serializers import user
from api.apps.task.models import (
    TaskProfile,
    
    )
from api.apps.task.models import user
from rest_framework.authentication import TokenAuthentication #Udemy
from rest_framework import generics
from django.contrib.auth.models import (
    User as AuthUser,
    )
import django_filters.rest_framework # Filters
from django_filters.rest_framework import DjangoFilterBackend

# from api.apps.task.serializers import TasksSerializer
from rest_framework import (
    permissions,
    status,
    viewsets,
    filters,
    )

from django.db.models import (
    Count,
    Value,
    F,
    Q
    )
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404


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


class ExportData(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        tasks = TaskProfile.objects.all()
        formato = request.GET.get('formato')
        serializer = TasksSerializer(tasks,many=True)
        formatos = {
            "json": self.get_json,
            "txt": self.get_txt
        }
        try:
            content, content_type = formatos[formato](serializer)
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="tasks.{formato}"'
            
            return response
        
        except KeyError:
            return Response({"detail": "Formato não suportado "},status=status.HTTP_400_BAD_REQUEST)

               
    def get_json(self, serializer):
        # Serializa os dados em JSON
        content = JSONRenderer().render(serializer.data)
        return content, "application/json"
    
    def get_txt(self, serializer):
        # Gera o conteúdo em formato de texto
        content = []
        for task in serializer.data:
            content.append(
                f'Titulo: {task["title"]}\n'
                f'Descricao: {task["description"]}\n'
                f'Prazo: {task["deadline"]}\n'
                f'Data de Lançamento: {task["release"]}\n'
                f'Concluida: {task["completed"]}\n'
                f'Finalizada Em: {task["finished_in"]}\n'
                f'Finalizada Por: {task["finished_by"]}\n'
                f'Criada Em: {task["created_in"]}\n'
                f'Atualizada: {task["updated"]}\n'
                f'Responsavel: {task["responsible"]}\n'
                '---\n'
            )
        content = ''.join(content)

        return content, 'text/plain; charset=utf-8'

class ExportFilters(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request, report_type, slug):
        created_by = request.GET.get('created_by')
        finished_by = request.GET.get('finished_by')
        responsible = request.GET.get('responsible')
        created_in = request.GET.get('created_in')
        fininshed_in = request.GET.get('finished_in')
        deadline = request.GET.get('deadline')
        
        # ----------- Maior que ou igual a -------- Menor que ou igual a ------
        filters_report = Q(deadline__gte=created_in) & Q(deadline__lte=fininshed_in)
        
        # Fazendo uma busca primária no Banco de Dados:
        tasks = TaskProfile.objects.filter(filters_report)
        
        # Boas práticas para dicionário, fez o mesmo com o txt/json
        report_types = {
            'created_and_finished_by_user': self.created_and_finished_by_user(tasks),
            'activites_by_responsible': self.activities_by_responsible(tasks),
            'activites_completed_after_the_deadline': self.activites_completed_after_the_dealine(tasks)
        }
        
        try:
            data = report_types[report_type](tasks)
            
            return Response(data,
                            status=status.HTTP_200_OK)
        
        except KeyError:
            return Response({'Release: Invalid Report'},
                            status=status.HTTP_400_BAD_REQUEST)
            
    def created_and_finished_by_user(self, tasks):
        created = tasks.values('created_by__username').annotate(total_created=Count('id'))
        finished = tasks.filter(completed=True).values('finished_by__username').annotate(total_finalished=Count('id'))

        data = {
            'created_by_user': list(created),
            'finished_by_user': list(finished)
        }
        return data
    
    def activities_by_responsible(self, tasks):
        activite_by_responsible = tasks.values('responsaveis__username').annotate(total_ativities=Count('id'))

        data = {
            'activities_by_responsible': list(activite_by_responsible)
        }
        return data   

    def activites_completed_after_the_dealine(self, tasks):
        today = datetime.today().date()
        late = tasks.filter(completed=False, deadline__lt=today).count()
        activities_completed_after_the_deadline = tasks.filter(completed=True, finished_in__date__gt=F('deadline')).count()

        data = {
            'late_activites': late,
            'activities_completed_after_the_deadline': activities_completed_after_the_deadline
        }
        return data
    
        

        # responsibles = user.TaskResponsible.objects.all()
        # serializer_responsibles = TaskResponsibleSerializer(responsibles, many=True)

        # tasks = TaskProfile.objects.all()
        # serializer_tasks = TasksSerializer(tasks, many=True)
        
        # content = self.filters()
        
        # response = HttpResponse(content, content_type='application/json')
        # response['Content-Disposition'] = 'attachment; filename="filters.json"'
        # return response
     
"""    def filters(self):
        num_responsibles = user.TaskResponsible.objects.count()
        num_tasks = TaskProfile.objects.count()
        num_users = AuthUser.objects.count()
        tasks = TaskProfile.objects.values(
            "responsible",
            name=Concat(F("responsible__first_name"),Value(" "), F("responsible__last_name"))
        ).annotate(cnt=Count("id")).values("responsible", "cnt", "name")
        print(tasks)
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
        return json_content"""

class TaskViewsSet(viewsets.ModelViewSet):
    serializer_class = TasksSerializer
    queryset = user.TaskProfile.objects.all()
    # filter_backends = (filters.SearchFilter,) simples
    # search_fields = ('title', 'release')
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['created_in', 'finished_in']
    


    
        # # Verificação: Minhas verificações já foram feitas nos serializ
        # if created_by:
        #     filters &= Q(created_by__id=created_by)
        # if finished_by:
        #     filters &= Q(finished_by__id=finished_by)
        # if responsible:
        #     filters &= Q(responsible__id=responsible)
