from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from apps.core.models import Admission, Medecin, MotifRdv


@login_required
@permission_required('core.change_patient', raise_exception=True)
def modifier_ordre(request, pk):
    nouvel_ordre = request.POST.get('ordre', None)
    adm = get_object_or_404(Admission, pk=pk)
    ancien_ordre = adm.ordre
    Admission.objects.filter(date__day=adm.date.day, date__month=adm.date.month, date__year=adm.date.year, statut='1',
                             patient__compte=request.user.profil.compte, ordre__gte=nouvel_ordre,
                             ordre__lt=ancien_ordre) \
        .update(ordre=F('ordre') + 1)

    Admission.objects.filter(date__day=adm.date.day, date__month=adm.date.month, date__year=adm.date.year, statut='1',
                             patient__compte=request.user.profil.compte, ordre__gt=ancien_ordre,
                             ordre__lte=ancien_ordre) \
        .update(ordre=F('ordre') - 1)
    adm.ordre = nouvel_ordre
    adm.save()
    admissions = Admission.objects.filter(date__day=adm.date.day, date__month=adm.date.month, date__year=adm.date.year,
                                          statut='1',
                                          patient__compte=request.user.profil.compte).order_by('ordre')
    print('Admissions', admissions)
    data = {'message': "Admissions réordonnées avec succès"}
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_admission(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    admission.statut = 10
    admission.save()
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return redirect('accueil')


def modifier_admission(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    praticien_id = request.POST.get('praticien', None)
    if praticien_id:
        praticien = get_object_or_404(Medecin, pk=praticien_id)
        admission.praticien = praticien
    motif_rdv_id = request.POST.get('motif', None)
    if motif_rdv_id:
        motif = get_object_or_404(MotifRdv, pk=motif_rdv_id)
        admission.motif = motif
    admission.save()
    data = {'message': "Admission modifiée avec succès"}
    return JsonResponse(data)