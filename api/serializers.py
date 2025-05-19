from rest_framework.serializers import ModelSerializer
from .models import Note
from rest_framework import serializers


class NoteSerializer(serializers.ModelSerializer):
    body = serializers.CharField(required=True, allow_blank=False)
    
    class Meta:
        model = Note
        fields = '__all__'

    def validate_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Body cannot be empty.")
        return value


