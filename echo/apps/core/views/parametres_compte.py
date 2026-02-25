import pytz
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import FormView, UpdateView

from apps.core.forms import ParametresGenerauxForm
from apps.core.models import ParametresCompte, Profil


class ParametresGeneraux(PermissionRequiredMixin, UpdateView):
    permission_required = 'core.change_parametrescompte'
    template_name = "core/parametres.html"
    form_class = ParametresGenerauxForm
    model = ParametresCompte

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timezones'] = pytz.common_timezones
        return context

    def get_initial(self):
        initial_base = super().get_initial()
        initial_base['compte'] = self.request.user.profil.compte
        return initial_base

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['compte'] = self.request.user.profil.compte
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            self.request.session['django_timezone'] = form.cleaned_data['timezone']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('parametres_generaux', kwargs={'pk': self.object.id})

