# Built in imports.
import json
# Third Party imports.
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
# Django imports.
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser
from django.db.models import F

from apps.chat.models import Dialog, Message
from apps.chat.serializers import MessageSerializer
from apps.core.models import Profil


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.discussion = self.scope['url_route']['kwargs']['id']
        print('Connected client, discussion', self.discussion)
        self.users = await self.get_users()
        print('Utilisateurs de la discussion', self.users)
        self.discussion_group = 'chat_{}'.format(self.discussion)
        # Join room group
        print('Joining group')
        await self.channel_layer.group_add(
            self.discussion_group,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        print('Received message', json.loads(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        msg = await self.creer_message(sender, message)
        await self.channel_layer.group_send(
            self.discussion_group,
            {
                'type': 'send_message',
                'message': msg
            }
        )
        print('Users', self.users)

    # Receive message from room group
    async def send_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

        for user in self.users:
            user_group = 'user_{}'.format(user.pk)
            await self.channel_layer.group_send(
                user_group,
                {
                    'type': 'incoming_msg',
                    'discussion': self.discussion
                }
            )

    async def disconnect(self, message):
        print('Disconnected client')
        # Leave room group
        await self.channel_layer.group_discard(
            self.discussion_group,
            self.channel_name
        )
        event = { 'message': '', 'type': 'opponent_disconnected'}
        await self.send_message(event)

    @database_sync_to_async
    def creer_message(self, sender, message):
        print('Creation message', self.discussion, sender, message)
        msg = Message.objects.create(dialog_id=self.discussion, sender_id=sender, text=message, read=False)
        return MessageSerializer(msg).data

    @database_sync_to_async
    def get_users(self):
        disc = Dialog.objects.get(pk=self.discussion)
        print('Discussion owner', disc.owner)
        print('Discussion opponent', disc.opponent)
        return [disc.owner, disc.opponent]


class EventConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['url_route']['kwargs']['id']
        print('Connected client, user', self.user)
        self.user_group = 'user_{}'.format(self.user)
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        await self.connecte(self.user)
        await self.accept()

    async def receive(self, text_data):
        print('Received message', json.loads(text_data))
        text_data_json = json.loads(text_data)

    async def incoming_msg(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'incoming_msg',
            'discussion': event['discussion']
        }))

    async def disconnect(self, message):
        print('Disconnected client')
        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )
        await self.deconnecte(self.user)

    @database_sync_to_async
    def connecte(self, user_pk):
        return Profil.objects.filter(pk=user_pk).update(enligne=1)

    @database_sync_to_async
    def deconnecte(self, user_pk):
        return Profil.objects.filter(pk=user_pk).update(enligne=0)
