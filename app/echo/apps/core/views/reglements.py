import json
from datetime import date
from typing import Dict, Any

from django.views import View
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.core import serializers
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.views.generic import CreateView, UpdateView, ListView, TemplateView
from apps.core.models import Admission, Prestation
from django.db.models import Q
from apps.core.models import Reglement, Patient, Praticien, LigneReglement, Facture, Medecin, Cloture, Consultation
from apps.core.forms import ReglementForm, PatientForm, PraticienForm, LigneReglementForm
from apps.core.serializers import PrestationSerializer, AdmissionSerializer, ReglementSerializer, MedecinSerializer, \
    ClotureSerializer, ReglementRapportSerializer, AdmissionRapportSerializer
from django.forms.formsets import formset_factory
from django.core import validators
from django import forms
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.db.models import Sum
from django.forms import inlineformset_factory


class ReglementList(LoginRequiredMixin, TemplateView):
    template_name = 'core/reglement_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        admissions = Admission.objects.filter(Q(date__day=today.day)
                                              & Q(date__month=today.month)
                                              & Q(date__year=today.year)
                                              & ~Q(statut=10)
                                              & Q(patient__deleted_at=None)
                                              & Q(patient__compte=self.request.user.profil.compte)).order_by('ordre')
        admissions_json = AdmissionRapportSerializer(admissions, many=True)
        context['admissions_json'] = json.dumps(admissions_json.data)
        prestations = Prestation.objects.filter(compte=self.request.user.profil.compte)
        reglements_caisse = Reglement.objects.filter(cloture__isnull=True)
        lastest_fact_pk = 1
        if Facture.objects.count() > 0:
            lastest_fact_pk = Facture.objects.latest('id').pk
        context['derniere_facture_id'] = lastest_fact_pk
        reglements_caisse_json = ReglementSerializer(reglements_caisse, many=True)
        context['reglements_caisse'] = json.dumps(reglements_caisse_json.data)
        caisses = Cloture.objects.all()
        caisse_cloture_json = ClotureSerializer(caisses, many=True)
        context['caisses'] = json.dumps(caisse_cloture_json.data)
        context['prestations'] = prestations
        return context


class ReglementRapportList(LoginRequiredMixin, TemplateView):
    template_name = 'core/reglement_rapport_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        reglements = Reglement.objects.all()\
            .select_related('patient')
        lst = []
        for q in reglements:
            if q.patient.mot_cle and q.patient.mot_cle is not None:
                mots = json.loads(q.patient.mot_cle)
                cles = map(lambda m: m['value'], mots)
                lst.extend(cles)
        mots_cles = list(set(lst))
        mot_patient = mots_cles
        context['mots_patients'] = mot_patient
        reglements_json = ReglementRapportSerializer(reglements, many=True)
        context['reglements_json'] = json.dumps(reglements_json.data)
        prestations = Prestation.objects.filter(compte=self.request.user.profil.compte)
        context['prestations'] = prestations
        return context


class ReglementCreate2(PermissionRequiredMixin, View):
    template_name = 'core/reglement_form.html'
    permission_required = 'core.add_reglement'

    def get(self, request, pk):

        admission = get_object_or_404(Admission, pk=pk)
        patient = get_object_or_404(Patient, pk=admission.patient.id)
        praticien = None
        today = date.today()
        consultations = patient.consultation_set.filter(Q(date__day=today.day)
                                                        & Q(date__month=today.month)
                                                        & Q(date__year=today.year))
        if len(consultations):
            praticien = consultations[0].praticien
        initial_reglement = {'admission': pk, 'patient': patient.pk, 'praticien': praticien, 'date_cheque': today,'mutuelle': patient.mutuelle}
        LigneFormSet = formset_factory(LigneReglementForm)
        reglement_form = ReglementForm(initial=initial_reglement)
        formset = LigneFormSet
        prestations = Prestation.objects.filter(compte=request.user.profil.compte).order_by('code')
        prestation_mutuelle=get_object_or_404(Prestation, code="C2")
        context = {
            'admission': admission,
            'reglement': reglement_form,
            'formset': formset,
            'praticien': praticien,
            'prestations': prestations,
            'prestation_mutuelle' : prestation_mutuelle,
            'patient': patient
        }
        if patient.mutuelle:
            prestation_par_defaut = Prestation.objects.filter(code="C2")
        else:
            prestation_par_defaut = Prestation.objects.filter(compte=request.user.profil.compte, par_defaut=True)
        if len(prestation_par_defaut):
            context['prestation_par_defaut'] = json.dumps(PrestationSerializer(prestation_par_defaut[0]).data)

        print('prestation_par_defaut', prestation_par_defaut)

        #context['historique'] = json.dumps(ReglementSerializer(patient.reglement_set, many=True).data)

        return render(request, self.template_name, context)

    def post(self, request, pk):
        LigneFormSet = formset_factory(LigneReglementForm)
        reglement_form = ReglementForm(request.POST)
        mutuelle_check = request.POST.get('mutuelle_checked')
        print(mutuelle_check)

        if mutuelle_check == "oui":
            condition=reglement_form.is_valid()
        else:
            ligne_formset = LigneFormSet(request.POST or None)
            condition = reglement_form.is_valid() and ligne_formset.is_valid()
        if condition:
            # return HttpResponse(total_prestation)
            espece = reglement_form.cleaned_data.get('espece_payment', None)
            cb = reglement_form.cleaned_data.get('cb_payment', None)
            cheque = reglement_form.cleaned_data.get('cheque_payment', None)
            total = 0
            total_prestation = request.POST.get('total', None)
            print('Total', total_prestation)
            if espece is not None:
                total += float(espece)
            if cb is not None:
                total += float(cb)
            if cheque is not None:
                total += float(cheque)
            print(total)
            if total != float(total_prestation.replace(",", ".")):
                msg = "Veuillez saisir une somme valide"
                if mutuelle_check == "oui":
                   context = {
                    'msg': msg,
                    'reglement': reglement_form
                   }
                else:
                    context = {
                        'msg': msg,
                        'reglement': reglement_form,
                        'formset': ligne_formset
                    }
                return render(request, self.template_name, context)

            reglement = reglement_form.save()
            nom_mutuelle = reglement_form.cleaned_data.get('nom_mutuelle')
            reglement.nom_mutuelle = nom_mutuelle
            reglement.save()
            new_lines = []
            if mutuelle_check == "non":
                for line_form in ligne_formset:
                    prestation_code = line_form.cleaned_data.get('code')
                    print('Recherche prestation {}'.format(prestation_code))
                    prestation = get_object_or_404(Prestation, code=prestation_code)
                    print('Prestation {} trouvée'.format(prestation_code))
                    prix = line_form.cleaned_data.get('prix_ttc')
                    if prestation_code and prix:
                        new_lines.append(
                        LigneReglement(prestation=prestation.prestation, code=prestation_code,
                                       prix_ttc=prix, prix_initial=prix,
                                       reglement=reglement))
            else:
                prestation = get_object_or_404(Prestation, code="C2")
                prix = prestation.prix_pec
                if prestation and prix:
                    new_lines.append(
                        LigneReglement(prestation=prestation.prestation, code=prestation.code,
                                       prix_ttc=prix,
                                       prix_initial=prestation.prix_ttc,
                                       reglement=reglement))
            try:
                with transaction.atomic():
                    # Replace the old with the new
                    LigneReglement.objects.bulk_create(new_lines)
                    # And notify our users that it worked
                    # return redirect("/reglement?msg=Reglement ajouté avec succés")

                    # And notify our users that it worked
                    messages.success(request, 'Reglement ajouté avec succés.')

            except IntegrityError:  # If the transaction failed
                messages.error(request, 'Error.')

            return redirect('reglements_list')
            # end if of validate
        if (mutuelle_check == "oui"):
            context = {
            'reglement': reglement_form
            }
        else:
            context = {
                'reglement': reglement_form,
                'formset': ligne_formset
            }
        return render(request, self.template_name, context)


LigneFormSet = inlineformset_factory(Reglement, LigneReglement,
                                     form=LigneReglementForm, fields='__all__',
                                     extra=1, can_delete=True)


class ReglementCreate(CreateView):
    template_name = 'core/reglement_form.html'
    model = Reglement
    form_class = ReglementForm
    success_url = reverse_lazy('reglements_list')
    init = {}

    def get_context_data(self, **kwargs):
        print('Get context data')

        admission = get_object_or_404(Admission, pk=self.kwargs['pk'])
        patient = get_object_or_404(Patient, pk=admission.patient.id)
        praticien = None
        today = date.today()
        consultations = patient.consultation_set.filter(Q(date__day=today.day)
                                                        & Q(date__month=today.month)
                                                        & Q(date__year=today.year))
        if len(consultations):
            praticien = consultations[0].praticien

        prestations = Prestation.objects.filter(compte=self.request.user.profil.compte).order_by('code')

        prestation_mutuelle = Prestation.objects.filter(compte=self.request.user.profil.compte, code="C2")

        self.init = {'admission': admission.pk,
                     'patient': patient.pk,
                     'praticien': praticien,
                     'date_cheque': today,
                     'mutuelle': patient.mutuelle}

        context = super().get_context_data(**kwargs)

        extra = 1
        LigneReglementFormset = inlineformset_factory(Reglement, LigneReglement,
                                                      form=LigneReglementForm, fields='__all__',
                                                      extra=extra, can_delete=True)
        if self.request.POST:
            context["formset"] = LigneReglementFormset(self.request.POST, instance=self.object)
        else:
            context["formset"] = LigneReglementFormset(instance=self.object)

        context['reglement'] = context["form"]
        context['patient'] = patient
        if prestation_mutuelle:
            context['prestation_mutuelle'] = prestation_mutuelle[0]
        context['prestations'] = prestations
        context['prestations_json'] = json.dumps(PrestationSerializer(prestations, many=True).data)
        context['praticien'] = praticien
        if patient.mutuelle and prestation_mutuelle:
            prestation_par_defaut = prestation_mutuelle
        else:
            prestation_par_defaut = Prestation.objects.filter(compte=self.request.user.profil.compte, par_defaut=True)
        if len(prestation_par_defaut):
            context['prestation_par_defaut'] = prestation_par_defaut[0]
            context['prestation_par_defaut_json'] = json.dumps(PrestationSerializer(prestation_par_defaut[0]).data)
        print('prestation_par_defaut', prestation_par_defaut)

        return context

    def get_initial(self):
        print('Get initial')
        init = super().get_initial()
        print("Initial", self.init)
        return {**init, **(self.init)}

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if formset.is_valid():
                    print('formset valid')
                    formset.instance = self.object
                    formset.save()
        else:
            print('Form not valid', form.errors)

        return super().form_valid(form)


class ReglementUpdate(UpdateView):

    template_name = 'core/reglement_form.html'
    model = Reglement
    form_class = ReglementForm
    success_url = reverse_lazy('reglements_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra = 1
        if self.object.lignes_reglement.count() > 0:
            extra = 0
        LigneReglementFormset = inlineformset_factory(Reglement, LigneReglement,
                                             form=LigneReglementForm, fields='__all__',
                                             extra=extra, can_delete=True)
        if self.request.POST:
            context["formset"] = LigneReglementFormset(self.request.POST, instance=self.object)
        else:
            context["formset"] = LigneReglementFormset(instance=self.object)

        print(">>>>>>>>>>>> Nb de lignes de règlement", len(self.object.lignes_reglement.all()))
        for l in self.object.lignes_reglement.all():
            print(l.code)

        prestations = Prestation.objects.filter(compte=self.request.user.profil.compte).order_by('code')
        context['prestations_json'] = json.dumps(PrestationSerializer(prestations, many=True).data)
        prestation_mutuelle = get_object_or_404(Prestation, code="C2")
        context['object'] = self.object
        context['reglement'] = context["form"]
        context['patient'] = self.object.patient
        context['prestation_mutuelle'] = prestation_mutuelle
        context['prestations'] = prestations
        patient = self.object.patient

        if patient.mutuelle:
            prestation_par_defaut = Prestation.objects.filter(code="C2")
        else:
            prestation_par_defaut = Prestation.objects.filter(compte=self.request.user.profil.compte, par_defaut=True)
        if len(prestation_par_defaut):
            context['prestation_par_defaut'] = prestation_par_defaut[0]
            context['prestation_par_defaut_json'] = json.dumps(PrestationSerializer(prestation_par_defaut[0]).data)
        print('prestation_par_defaut', prestation_par_defaut)

        return context


    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                print('form valid')
                if formset.is_valid():
                    print('formset valid')
                    formset.instance = self.object
                    formset.save()
        else:
            print('Form not valid', form.errors)

        return super().form_valid(form)



class ReglementUpdate2(PermissionRequiredMixin, View):
    template_name = 'core/reglement_form.html'
    permission_required = 'core.change_reglement'

    def get(self, request, pk):
        reglement = get_object_or_404(Reglement, pk=pk)
        patient = get_object_or_404(Patient, pk=reglement.patient.id)
        ligne_reglement = LigneReglement.objects.filter(reglement=reglement.pk).values()
        print(">>>>>>>>>>>> Nb de lignes de règlement", len(ligne_reglement))
        reglement_form = ReglementForm(instance=reglement)

        #LigneFormSet = formset_factory(LigneReglementForm, extra=0)
        formset = LigneFormSet(instance=reglement)

        prestations = Prestation.objects.filter(compte=request.user.profil.compte).order_by('code')
        prestation_mutuelle = get_object_or_404(Prestation, code="C2")
        context = {
            'object': reglement,
            'reglement': reglement_form,
            'patient': patient,
            'formset': formset,
            'prestation_mutuelle': prestation_mutuelle,
            'prestations': prestations
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        LigneFormSet = formset_factory(LigneReglementForm)
        reglement = get_object_or_404(Reglement, pk=pk)
        reglement_form = ReglementForm(request.POST, instance=reglement)
        ligne_formset = LigneFormSet(request.POST or None)
        mutuelle_check = request.POST.get('mutuelle_checked')

        if reglement_form.is_valid() and ligne_formset.is_valid():
            # return HttpResponse(total_prestation)
            espece = reglement_form.cleaned_data.get('espece_payment', None)
            cb = reglement_form.cleaned_data.get('cb_payment', None)
            cheque = reglement_form.cleaned_data.get('cheque_payment', None)
            total = 0
            total_prestation = request.POST.get('total', None)
            print(total_prestation)
            if espece is not None:
                total += float(espece)
            if cb is not None:
                total += float(cb)
            if cheque is not None:
                total += float(cheque)
            if total != float(total_prestation.replace(",", ".")):
                msg = "Veuillez saisir une somme valide"
                context = {
                    'msg': msg,
                    'reglement': reglement_form,
                    'formset': ligne_formset
                }
                return render(request, self.template_name, context)
            reglement = reglement_form.save()
            query = LigneReglement.objects.filter(reglement=reglement.pk)
            query.delete()
            new_lines = []

            for line_form in ligne_formset:
                print('Ligne formset', line_form.cleaned_data.get('code'))
                obj = line_form.save(commit=False)
                continue
                if mutuelle_check == "oui":
                    prestation = get_object_or_404(Prestation, code="C2")
                    obj.prix_initial = prestation.prix_ttc
                    obj.prestation = prestation.prestation
                else:
                    prestation_code = line_form.cleaned_data.get('code')
                    prestation = get_object_or_404(Prestation, code=prestation_code)
                    obj.prestation = prestation.prestation
                obj.reglement = reglement
                obj.save()

            """
            try:
                with transaction.atomic():
                    # Replace the old with the new
                    LigneReglement.objects.bulk_create(new_lines)
                    # And notify our users that it worked
                    # return redirect("/reglement?msg=Reglement ajouté avec succés")

                    # And notify our users that it worked
                    messages.success(request, 'Reglement ajouté avec succés.')

            except IntegrityError:  # If the transaction failed
                messages.error(request, 'Error.')
            """

            if 'next' in request.GET:
                return redirect(request.GET['next'])
            else:
                return redirect('reglements_list')
        # end if of validate
        context = {
            'reglement': reglement_form,
            'formset': ligne_formset
        }
        return render(request, self.template_name, context)


@permission_required('core.add_facture', raise_exception=True)
def facture_create(request, pk):
    reglement = get_object_or_404(Reglement, pk=pk)
    facture = Facture(reglement=reglement)
    facture.save()
    data = {
        'pk': facture.pk,
        'message': "Facture ajouté"
    }
    return JsonResponse(data)


@permission_required('core.add_cloture', raise_exception=True)
def caisse_cloture(request):
    caisse = Cloture()
    caisse.save()
    reglement_array = request.POST.getlist('reglements_ids[]', None)
    for reglement in reglement_array:
        object = get_object_or_404(Reglement, pk=reglement)
        object.cloture = caisse
        object.save()
    return redirect(reverse("cloture_detail", kwargs={'pk': caisse.pk}))


class ClotureDetail(LoginRequiredMixin, TemplateView):
    template_name = 'core/cloture_detail.html'
    permission_required = 'core.view_cloture'

    def get_context_data(self, *args, **kwargs):
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        cloture_reglements = Reglement.objects.filter(cloture=self.kwargs['pk'])
        sum_espece = list(Reglement.objects.filter(cloture=self.kwargs['pk']).aggregate(Sum('espece_payment')).values())[0]
        sum_cb = list(Reglement.objects.filter(cloture=self.kwargs['pk']).aggregate(Sum('cheque_payment')).values())[0]
        sum_cheque = list(Reglement.objects.filter(cloture=self.kwargs['pk']).aggregate(Sum('cb_payment')).values())[0]
        cloture_reglements_json = ReglementSerializer(cloture_reglements, many=True)
        context['cloture'] = Cloture.objects.get(pk=self.kwargs['pk'])
        context['cloture_reglements'] = json.dumps(cloture_reglements_json.data)
        if sum_espece:
            context['sum_espece'] = sum_espece
        else:
            context['sum_espece'] = 0
        if sum_cb:
            context['sum_cb'] = sum_cb
        else:
            context['sum_cb'] = 0
        if sum_cheque:
            context['sum_cheque'] = sum_cheque
        else:
            context['sum_cheque'] = 0
        total = 0
        if sum_espece:
            total += sum_espece
        if sum_cheque:
            total += sum_cheque
        if sum_cb:
            total += sum_cb
        context['total'] = total

        return context
