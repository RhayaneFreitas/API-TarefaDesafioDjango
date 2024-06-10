from rest_framework import serializers
from api.apps.task.models import (
    TaskProfile,
    #TaskResponsible
)
from django.db.models import Q
from api.apps.task.models import task
from rest_framework import (
    status,
    viewsets,
    filters,
)

from rest_framework.validators import UniqueValidator
import re
import datetime
from django.utils.translation import gettext_lazy as _

class TasksSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TaskProfile
        fields = (
            "id",
            "title",
            "description",
            "deadline",
            "created_in",
            "created_by",
            "updated",
            "release",
            "completed",
            "finished_in",
            "finished_by",
            "responsible",
            
        )
        
        read_only_fields = (
            'id',
        )
    def validate_title(self, verification):
        if not verification:
            raise serializers.ValidationError(
                {
                    'Release': _("O título é obrigatório.")
                }
            )
        if re.search(r'[^A-Za-z\s]', verification):
            raise serializers.ValidationError(
                {
                    'Release': _("O título não pode conter somente números ou caracteres especiais.")
                }
            )
        return verification
    
    def validate_release(self, verification):
        if verification.year < 2000:
            raise serializers.ValidationError(
                {
                    'Release:': _("O ano não pode ser anterior ao ano de 2000.")
                    
                }
            )
        return verification
    
    def validate_deadline(self, verification):
        if verification.year < 2000:
            raise serializers.ValidationError(
                {
                    'Release:': _("O ano não pode ser anterior ao ano de 2000.")
                    
                }
            )
        return verification

    def validate_future_date(self, verification):
        if verification > datetime.date.today():
            raise serializers.ValidationError(
                {
                    'Release': _('A data não se pode estar no futuro')
                }
            )
        return verification
    
    def validate_created_in(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError(
                {
                    'Release': _("A data de criação não pode ser anterior ao dia de hoje.")
                }
            )
        if value > datetime.date.today():
            raise serializers.ValidationError(
                {
                    'Release': _("A data de criação não pode ser no futuro.")
                }
            )
        return value    
    
    def validate_finished_in(self, value):
        if value and value < datetime.date.today():
            raise serializers.ValidationError(
                {
                    'Release': _("A data de finalização não pode ser anterior ao dia de hoje.")
                }
            )
        return value
    
    # def validate(self, data):
    #     created_date = data.get('created_in')
    #     finished_date = data.get('finished_in')
        
    #     if created_date and finished_date:
    #         difference = created_date - finished_date
    #         if difference.days > 365:
    #             raise serializers.ValidationError(
    #                 {
    #                     'Release': _("O período entre as datas não pode ser maior que 365 dias.")
    #                 }
    #             )

    #     elif created_date or finished_date:
    #         raise serializers.ValidationError(
    #             {
    #                 'Release': _("data de criação e data final são obrigatórios.")
    #             }
    #         )
        
    #     return data

# Tentando refinar o Código:
class TaskReportFilterSerializer(serializers.Serializer):
    created_in = serializers.DateField(
        required=True
    )
    finished_in = serializers.DateField(
        required=True
    )
    created_by = serializers.IntegerField(
        required=False, allow_null=True
    )
    finished_by = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    responsible = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    def validate(self, data):
        created_in = data.get('created_in')
        finished_in = data.get('finished_in')

        if created_in and finished_in:
            if (finished_in - created_in).days > 365:
                raise serializers.ValidationError(
                    _("O período entre as datas não pode ser maior que 365 dias.")
                )
        else:
            raise serializers.ValidationError(
                _("As datas de criação e finalização são obrigatórias.")
            )
        
        return data

    # def get_filters(self):
    #     filters = Q(deadline__gte=self.validated_data['created_in']) & Q(deadline__lte=self.validated_data['finished_in'])

    #     if self.validated_data.get('created_by'):
    #         filters &= Q(created_by__id=self.validated_data['created_by'])
    #     if self.validated_data.get('finished_by'):
    #         filters &= Q(finished_by__id=self.validated_data['finished_by'])
    #     if self.validated_data.get('responsible'):
    #         filters &= Q(responsible__id=self.validated_data['responsible'])

    #     return filters    
    
class TaskResponsibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = task.TaskResponsible
        fields = (
            "user",
            "task"   
        )

