from django import forms
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.utils.datastructures import MultiValueDict

class ArrayFieldCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """This is a Form Widget for use with a Postgres ArrayField. It implements
    a multi-select interface that can be given a set of `choices`.
    You can provide a `delimiter` keyword argument to specify the delimeter used.
    """
    def __init__(self, *args, **kwargs):
        # Accept a `delimiter` argument, and grab it (defaulting to a comma)
        self.delimiter = kwargs.pop('delimiter', ',')
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        if isinstance(data, MultiValueDict):
            # Normally, we'd want a list here, which is what we get from the
            # SelectMultiple superclass, but the SimpleArrayField expects to
            # get a delimited string, so we're doing a little extra work.
            print('Data', data.getlist(name))
            return data.getlist(name)

        return data.get(name)

    def get_context(self, name, value, attrs):
        print('Splited', value.split(self.delimiter))
        return super().get_context(name, value.split(self.delimiter), attrs)
