from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import json
from datetime import (
    datetime,
    timedelta,
    date
)
from api.apps.task.serializers.user import (
    TasksSerializer,
    TaskResponsibleSerializer,
    TaskReportFilterSerializer
    )
from api.apps.task.serializers import user
from api.apps.task.models import (
    TaskProfile,
    
    )
from api.apps.task.models import task
from rest_framework.authentication import TokenAuthentication #Udemy
from rest_framework import generics
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

#Entendendo parte Agregate Django:
from django.db.models.aggregates import (
    Avg,
    Sum,
    Count,
    Min,
    Max
)
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from openpyxl import Workbook
from io import BytesIO # Prepara o arquivo para ser enviado como resposta

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
            "txt": self.get_txt,
            "excel": self.get_excel
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
    
    def get_excel(self, serializer):

        wb = Workbook() # -> Permite ler e Escrever Arquivo em Excel
        ws = wb.active # Representa o Arquivo em Excel

        # Adiciona os cabeçalhos
        headers = ["Titulo", "Descricao", "Prazo", "Data de Lançamento", "Concluida", 
                   "Finalizada Em", "Finalizada Por", "Criada Em", "Atualizada", "Responsavel"]
        ws.append(headers)

        # Adiciona os dados
        for task in serializer.data: # Tentar lapidar, Fernando não gosta de for.
            ws.append([
                task["title"], task["description"], task["deadline"], task["release"], task["completed"], 
                task["finished_in"], task["finished_by"], task["created_in"], task["updated"], task["responsible"]
            ])

        # Salva o arquivo em um objeto de bytes

        excel_file = BytesIO() # Manipula os dados binários como se forsse um arquivo.
        wb.save(excel_file)
        excel_file.seek(0) # Salva o conteúdo

        return excel_file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' # Captura todo o conteúdo do Arquivo

class TaskReportFilters(APIView):
    
    def get(self, request, report_type):
        serializer = TaskReportFilterSerializer(data=request.GET)
        if serializer.is_valid():
            filters = serializer.get_filters()
            tasks = TaskProfile.objects.filter(filters)

            report_types = {
                'created_and_finished_by_user': self.created_and_finished_by_user,
                'activites_by_responsible': self.activities_by_responsible,
                'activites_completed_after_the_deadline': self.activites_completed_after_the_dealine
            }

            try:
                data = report_types[report_type](tasks)
                
                return Response(data, status=status.HTTP_200_OK)
            
            except KeyError:
                return Response({'Release': 'O tipo de relatório fornecido é inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def created_and_finished_by_user(self, tasks):
        created = tasks.values('created_by__user').annotate(total_created=Count('id'))
        finished = tasks.filter(completed=True).values('finished_by__user').annotate(total_finished=Count('id'))

        data = {
            'created_by_user': list(created),
            'finished_by_user': list(finished)
        }
        return data

    def activities_by_responsible(self, tasks):
    # Gerar Lista de tarefas que possuem mais de 1 responsavel:
         # list_activities_by_autor = tasks.objects.annotate(num_responsible=Count("responsible")).filter(num_responsible__gt=1)
        
        activities_by_responsible = tasks.values('responsible__user').annotate(total_activities=Count('id'))

        data = {
            'activities_by_responsible': list(activities_by_responsible)
            
        }
        return data

    def activites_completed_after_the_dealine(self, tasks):
        today = date.today()
        late = tasks.filter(completed=False, deadline__lt=today).count()
        completed_after_deadline = tasks.filter(completed=True, finished_in__date__gt=F('deadline')).count()

        data = {
            'late_tasks': late,
            'activities_completed_after_the_deadline': completed_after_deadline
        }
        return data
    
    
# Atividade: Separar as atividades por Classe:
# class BaseReport:
#     def __init__(self, tasks):
#         self.tasks = tasks

#     def generate_report(self):
#         raise NotImplementedError # -> Deve implementar na subclasse

# class CreatedAndFinishedByUserReport(BaseReport):
#     def generate_report(self):
#         created = self.tasks.values('created_by__user').annotate(total_created=Count('id'))
#         finished = self.tasks.filter(completed=True).values('finished_by__user').annotate(total_finished=Count('id'))

#         data = {
#             'created_by_user': list(created),
#             'finished_by_user': list(finished)
#         }
#         return data

# class ActivitiesByResponsibleReport(BaseReport):
#     def generate_report(self):
#         activities_by_responsible = self.tasks.values('responsible__user').annotate(total_activities=Count('id'))

#         data = {
#             'activities_by_responsible': list(activities_by_responsible)
#         }
#         return data

# class ActivitiesCompletedAfterDeadlineReport(BaseReport):
#     def generate_report(self):
#         today = date.today()
#         late = self.tasks.filter(completed=False, deadline__lt=today).count()
#         completed_after_deadline = self.tasks.filter(completed=True, finished_in__date__gt=F('deadline')).count()

#         data = {
#             'late_tasks': late,
#             'activities_completed_after_the_deadline': completed_after_deadline
#         }
#         return data    
    

class TaskViewsSet(viewsets.ModelViewSet):
    serializer_class = TasksSerializer
    queryset = task.TaskProfile.objects.all()
    # filter_backends = (filters.SearchFilter,) simples
    # search_fields = ('title', 'release')
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['created_in', 'finished_in']
    
