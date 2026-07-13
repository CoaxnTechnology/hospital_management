import math


class AjaxTemplateMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.is_ajax():
            self.template_name = self.ajax_template_name
            return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)


def pretty_duration(days):
    res = ""
    d = math.floor(days / 365)
    if d > 1:
        res = f"{d} ans"
    elif d == 1:
        res = f"{d} an"

    m = math.floor((days % 365)/30)
    if m > 0:
        if res != "":
            res = res + " et "
        res = res + f"{m} mois"
    return res


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'