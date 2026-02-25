from rest_framework import serializers

from apps.chat.models import Dialog, Message
from apps.core.serializers import ProfilSerializer


class DialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dialog
        fields = '__all__'
        depth = 1

class DialogSerializerExt(serializers.ModelSerializer):
    num_messages = serializers.IntegerField()

    class Meta:
        model = Dialog
        fields = '__all__'
        depth = 1


class MessageSerializer(serializers.ModelSerializer):
    sender = ProfilSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        depth = 1
