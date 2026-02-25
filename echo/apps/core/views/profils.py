from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
# Create your views here.
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from apps.core.forms import ProfilFormset, UserForm, MdpForm, UserUpdateForm
from apps.core.models import Profil


class ProfilList(PermissionRequiredMixin, ListView):
    model = Profil
    permission_required = 'core.view_profil'

    def get_queryset(self):
        return Profil.objects.filter(compte=self.request.user.profil.compte)\
            .select_related('user')\
            .order_by('user__last_name')


class ProfilCreate(PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'core/profil_form.html'
    permission_required = 'core.add_profil'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["profil"] = ProfilFormset(self.request.POST, files=self.request.FILES)
        else:
            data["profil"] = ProfilFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        if form.is_valid():
            profils = context["profil"]
            self.object = form.save()
            self.object.set_password(form.cleaned_data['password'])
            self.object.save()
            if profils.is_valid():
                profils.instance = self.object
                instances = profils.save(commit=False)
                for instance in instances:
                    instance.compte = self.request.user.profil.compte
                    instance.save()

            user = self.object
            if not hasattr(user, 'profil'):
                user.profil = Profil()
                user.profil.compte = self.request.user.profil.compte
                user.profil.save()

            user.groups.clear()
            user.groups.add(form.cleaned_data['group'])

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("profils_list")


class ProfilUpdate(PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    context_object_name = 'edited_user'
    template_name = 'core/profil_form.html'
    permission_required = 'core.change_profil'

    def get_initial(self):
        initial_base = super(ProfilUpdate, self).get_initial()
        if self.object:
            initial_base['group'] = self.object.groups.all()[0]
        return initial_base

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['profil'] = ProfilFormset(self.request.POST, instance=self.object, files=self.request.FILES)
        else:
            data['profil'] = ProfilFormset(instance=self.object)

        if 'msg' in self.request.GET:
            if self.request.GET['msg'] == 'mdp_succes':
                data['msg'] = 'Mot de passe changé avec succès'

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        if form.is_valid():
            profils = context["profil"]
            self.object = form.save()
            profils.instance = self.object
            if profils.is_valid():
                instances = profils.save(commit=False)
                for instance in instances:
                    instance.compte = self.request.user.profil.compte
                    instance.save()
            else:
                print('Profil non valide')

            user = self.object
            user.groups.clear()
            user.groups.add(form.cleaned_data['group'])

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("profils_list")


@login_required
@permission_required('core.delete_profil', raise_exception=True)
def supprimer_profil(request, pk):
    try:
        query = User.objects.get(pk=pk)
        query.delete()
        return redirect('profils_list')
    except:
        return HttpResponseNotFound()


class MotDePasseUpdate(BSModalUpdateView):
    template_name = 'core/mdp_form.html'
    permission_required = 'core.change_profil'
    form_class = MdpForm
    success_message = 'Mot de passe modifié avec succès.'
    success_url = reverse_lazy('accueil')
    model = User

    def get_initial(self):
        initial_base = super().get_initial()
        initial_base['password'] = ''
        return initial_base

    def form_valid(self, form):
        if form.is_valid():
            print('Nouveau pass', form.cleaned_data['password'])
            self.object.set_password(form.cleaned_data['password'])
            self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET['next']
