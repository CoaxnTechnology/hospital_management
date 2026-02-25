from django.urls import path

from .views import liste_utilisateurs, liste_discussions, creer_discussion, liste_messages, marquer_messages_lus

urlpatterns = [
    path('liste_utilisateurs', liste_utilisateurs, name='utilisateurs_liste'),
    path('liste_discussions/<int:pk>', liste_discussions, name='discussions_liste'),
    path('discussions/ajouter', creer_discussion, name='discussion_creer'),
    path('discussions/<int:discussion_pk>/messages', liste_messages, name='messages_liste'),
    path('discussions/<int:discussion_pk>/messages_lus', marquer_messages_lus, name='marquer_messages_lus')
]