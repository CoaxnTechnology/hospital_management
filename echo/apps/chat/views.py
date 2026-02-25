from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from apps.chat.models import Dialog, Message
from apps.chat.serializers import DialogSerializer, MessageSerializer, DialogSerializerExt
from apps.core.models import Profil
from apps.core.serializers import ProfilSerializer


@login_required
def liste_utilisateurs(request):
    profils = Profil.objects.filter(compte=request.user.profil.compte).order_by('-user__last_name')
    profils_json = ProfilSerializer(profils, many=True)
    data = {'users': profils_json.data}
    return JsonResponse(data)


@login_required
def liste_discussions(request, pk):
    discussions = Dialog.objects.filter(Q(owner=pk) | Q(opponent=pk))\
                        .annotate(num_messages=Count('messages', filter=Q(messages__read=False) & ~Q(messages__sender=pk)))
    #print('Discussions pour utilisateur {} - {}'.format(pk, len(discussions)))
    #for disc in discussions:
    #    print('>>> Discussion {} - {} vs {}'.format(disc.pk, disc.owner, disc.opponent))

    #discussions2 = Dialog.objects.filter(Q(owner=pk) | Q(opponent=pk))
    #print('Discussions 2', len(discussions2))
    discussions_json = DialogSerializerExt(discussions, many=True)
    #messages = Message.objects.filter(Q(discussion__owner=pk) | Q(discussion__opponent=pk), )
    data = {'discussions': discussions_json.data}
    return JsonResponse(data)


@login_required
def creer_discussion(request):
    owner_pk = request.POST.get('owner', None)
    opponent_pk = request.POST.get('opponent', None)
    #print('Creer discussion entre', owner_pk, opponent_pk)
    owner = get_object_or_404(Profil, pk=owner_pk)
    opponent = get_object_or_404(Profil, pk=opponent_pk)
    disc = Dialog(owner=owner, opponent=opponent)
    disc.save()
    return JsonResponse({'discussion': DialogSerializer(disc).data})


@login_required
def liste_messages(request, discussion_pk):
    discussion = get_object_or_404(Dialog, pk=discussion_pk)
    messages_json = MessageSerializer(discussion.messages.order_by('created'), many=True)
    data = {'messages': messages_json.data}
    return JsonResponse(data)

@login_required
def marquer_messages_lus(request, discussion_pk):
    discussion = get_object_or_404(Dialog, pk=discussion_pk)
    receiver_pk = request.POST.get('receiver', None)
    discussion.messages.filter(~Q(sender=receiver_pk)).update(read=True)
    data = {}
    return JsonResponse(data)
