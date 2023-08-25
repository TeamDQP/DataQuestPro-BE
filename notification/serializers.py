from rest_framework import serializers
from .models import EmailRecord


class EmailRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailRecord
        fields = ['targets', 'purpose']