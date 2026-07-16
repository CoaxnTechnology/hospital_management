# -*- coding: utf-8 -*-

from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.conf import settings
from django.template.defaultfilters import date as dj_date
from django.utils.translation import gettext as _
from django.utils.timezone import localtime

from apps.core.models import Profil


class Dialog(TimeStampedModel):
    owner = models.ForeignKey(Profil, verbose_name=_("Dialog owner"), related_name="selfDialogs",
                              on_delete=models.CASCADE)
    opponent = models.ForeignKey(Profil, verbose_name=_("Dialog opponent"), on_delete=models.CASCADE)

    def __str__(self):
        return _("Discussion avec ") + self.opponent.nom


class Message(TimeStampedModel, SoftDeletableModel):
    dialog = models.ForeignKey(Dialog, verbose_name=_("Dialog"), related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(Profil, verbose_name=_("Author"), related_name="messages",
                               on_delete=models.CASCADE)
    text = models.TextField(verbose_name=_("Message text"))
    read = models.BooleanField(verbose_name=_("Read"), default=False)
    all_objects = models.Manager()

    def get_formatted_create_datetime(self):
        return dj_date(self.created, settings.DATETIME_FORMAT)

    def __str__(self):
        return self.sender.nom + "(" + self.get_formatted_create_datetime() + ") - '" + self.text + "'"
