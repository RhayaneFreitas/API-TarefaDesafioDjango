from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from django.utils import timezone
from api.apps.task.serializers.user import (
    TasksSerializer,
    ActiviteByUserSerializer,
    UserLateTasksSerializer,
    UserCreatedAndFinishedTasksSerializer,
    TasksByUserSerializer
    )
from api.apps.task.models import (
    TaskProfile,
    User,
    )
from api.apps.task.reports import ReportExcel
from api.apps.task.models import task
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from rest_framework import (
    permissions,
    status,
    viewsets,
    )
from django.db.models import (
    Count,
    F,
    Q
    )
from django.db.models.aggregates import (
    Count,
    )

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
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def put(self, request, pk):
        try:
            task = TaskProfile.objects.get(pk=pk)
        except TaskProfile.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TasksSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

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
            return Response(
                {
                    "detail": _("Formato não suportado")
                },
                status=status.HTTP_400_BAD_REQUEST
            )

               
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

class ReportMixin:
    def get(self, request):
        format = request.GET.get('formato')
        queryset = self.get_queryset()
        
        serializer = self.serializer(queryset, many=True)
        
        choices = {
            'excel': self.export_to_excel,
            'json': self.export_to_json
        }
        
        try:
            return choices[format](serializer)
        
        except KeyError:
            return Response(
                {
                    "detail": _("Formato não suportado.")
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def export_to_excel(self, serializer):
        data = [
            list(data.values()) for data in serializer.data
        ]
        
        excel = ReportExcel(self.title, self.columns, data)
        
        return excel.export()
    
    def export_to_json(self, serializer):
        return Response(serializer.data)

class TasksCreatedFinishedByUserView(ReportMixin, APIView):
    
    serializer = TasksByUserSerializer
    title = "Tasks Created and Finished by User Report"
    columns = ["ID", "Name", "Tasks Created", "Tasks Finished"]

    def get_queryset(self):
        created_by = self.request.GET.get('created_by')
        finished_by = self.request.GET.get('finished_by')

        if not created_by and not finished_by:
            # Se nenhum filtro específico for aplicado, retornar todos os dados
            users = User.objects.all()
            queryset = []
            for user in users:
                created_task_count = TaskProfile.objects.filter(created_by=user).count()
                finished_task_count = TaskProfile.objects.filter(finished_by=user).count()
                queryset.append({
                    'id': user.id,
                    'name': user.name,
                    'tasks_created': created_task_count,
                    'tasks_finished': finished_task_count
                })
        else:
            queryset = []
            if created_by:
                created_task_count = TaskProfile.objects.filter(created_by_id=created_by).count()
                queryset.append({
                    'id': created_by,
                    'name': User.objects.get(id=created_by).name,
                    'tasks_created': created_task_count,
                    'tasks_finished': 0
                })

            elif finished_by:
                finished_task_count = TaskProfile.objects.filter(finished_by_id=finished_by).count()
                queryset.append({
                    'id': finished_by,
                    'name': User.objects.get(id=finished_by).name,
                    'tasks_created': 0,
                    'tasks_finished': finished_task_count
                })

        return queryset

class UserFinishedOwnTasksView(ReportMixin, APIView):
    
    queryset = User.objects.all()
    serializer = ActiviteByUserSerializer
    title = "User Finished Own Tasks Report"
    columns = ["ID", "Name", "Own Finished Count"]
    
    def get_queryset(self):
        return User.objects.annotate(
            task_count=Count('tasks_responsible', filter=Q(tasks_responsible__finished_by=F('pk')))
        ).values('id', 'name', 'task_count')
        
class ActivitiesByResponsibleView(ReportMixin, APIView):

    queryset = User.objects.all()
    serializer = ActiviteByUserSerializer
    title = "Number of activities per person responsible"
    columns = ["ID", "Name", "Activities by Responsible"]
    
    def get_queryset(self):
        return User.objects.annotate(
            task_count=Count('tasks_responsible')
        ).values('id', 'name', 'task_count').order_by('-task_count')
    
class LateTasksView(ReportMixin, APIView):
    
    queryset = User.objects.all()
    serializer = UserLateTasksSerializer
    title = "Late Tasks Report"
    columns = ["ID", "name", "late_count", "finished_late_count"]
    
    def get_queryset(self):
        current_date = timezone.now().date()
        return User.objects.annotate(
            late_count=Count('tasks_responsible', filter=Q(tasks_responsible__deadline__lt=current_date, tasks_responsible__completed=False)),
            finished_late_count=Count('tasks_responsible', filter=Q(tasks_responsible__deadline__lt=F('tasks_responsible__finished_in')))
        ).values('id', 'name', 'late_count', 'finished_late_count')
    
class UserCreatedAndFinishedTasksView(ReportMixin, APIView):
    
    queryset = User.objects.all()
    serializer = UserCreatedAndFinishedTasksSerializer
    title = "User Created and Finished Tasks Report"
    columns = ["ID", "name", "created_and_finished_count"]
    
    def get_queryset(self):
        return User.objects.annotate(
            created_and_finished_count=Count('task_profiles_created', filter=Q(task_profiles_created__finished_by=F('pk')))
        ).values('id', 'name', 'created_and_finished_count')

class TaskViewsSet(viewsets.ModelViewSet):
    serializer_class = TasksSerializer
    queryset = task.TaskProfile.objects.all()
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['created_in', 'finished_in']
# ---------------------------------------------------------------------------------------------------------------------------------

