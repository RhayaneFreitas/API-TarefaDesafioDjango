from rest_framework import serializers
from api.apps.task.models import (
    TaskProfile,
    #TaskResponsible
)
from api.apps.task.models import user
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
            "release",
            "description",
            "completed",
            "created_by",
            "finished_in",
            "finished_by",
            "created_in",
            "updated",
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
                    'Release': _("O título não pode conter números ou caracteres especiais.")
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
    
    def validate(self, data):
        created_date = data.get('created_in')
        finished_date = data.get('finished_in')
        
        if created_date and finished_date:
            difference = created_date - finished_date
            if difference.days > 365:
                raise serializers.ValidationError(
                    {
                        'Release': _("O período entre as datas não pode ser maior que 365 dias.")
                    }
                )
        return data   
    
    def validate_finished_in(self, value):
        if value and value < datetime.date.today():
            raise serializers.ValidationError(
                {
                    'Release': _("A data de finalização não pode ser anterior ao dia de hoje.")
                }
            )
        return value
    
class TaskResponsibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = user.TaskResponsible
        fields = (
            "user",
            "task"   
        )

