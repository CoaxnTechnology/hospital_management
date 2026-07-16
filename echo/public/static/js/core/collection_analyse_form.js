let KTDualListbox = function () {
    // Private functions
    let initDualListbox = function () {
        // Dual Listbox
        let listBoxes = $('.dual-listbox');

        listBoxes.each(function () {
            let $this = $(this);
            // get titles
            let availableTitle = 'Analyses disponibles';
            let selectedTitle = 'Analyses sélectionnées';

            // get button labels
            let addLabel = 'Ajouter';
            let removeLabel = 'Supprimer';
            let addAllLabel = 'Tout ajouter';
            let removeAllLabel = 'Tout supprimer';

            // get search option
            let search = ($this.attr('data-search') != null) ? $this.attr('data-search') : '';

            // init dual listbox
            let dualListBox = new DualListbox($this.get(0), {
                addEvent: function (value) {
                    console.log(value);
                    $('#btn-enregistrer').prop('disabled', false);
                },
                removeEvent: function (value) {
                    console.log(value);
                    if ($(this.selectedList).children('li').length == 1) {
                        $('#btn-enregistrer').prop('disabled', true);
                    }
                },
                availableTitle: availableTitle,
                selectedTitle: selectedTitle,
                addButtonText: addLabel,
                removeButtonText: removeLabel,
                addAllButtonText: addAllLabel,
                removeAllButtonText: removeAllLabel,

            });

            if (search == 'false') {
                dualListBox.search.classList.add('dual-listbox__search--hidden');
            }
            $('.dual-listbox__search')
                .addClass(['form-control', 'form-control-sm'])
                .attr('placeholder', 'Recherche');

            if ($(dualListBox.selectedList).children('li').length > 0) {
                $('#btn-enregistrer').prop('disabled', false);
            }
        });
    };

    return {
        // public functions
        init: function () {
            initDualListbox();
        },
    };
}();

$(document).ready(function () {

    $('#id_analyses option').each((idx, el) => {
        //$(el).attr('data-order', $(el).attr('value'));
        if (_.find(analyses_ajoutees, i => i.id == el.value))
            $(el).remove();
    });
    _.each(analyses_ajoutees,
            i => $('#id_analyses').prepend(`<option value="${i.id}" selected>${i.code} - ${i.libelle}</option>`));
    KTDualListbox.init();

    $('#btn-enregistrer').click(e => {
        e.preventDefault();
        if ($('#id_nom').val().trim() == "") return;

        data = $('form').serialize();
        data = data.substr(0, data.indexOf('analyses'));
        let ordre = '&ordre=';
        $($('.dual-listbox__selected .dual-listbox__item').get()).each((idx, el) => {
            const id = $(el).attr('data-id');
            data += 'analyses=' + id + '&';
            ordre += `${id}+`;
        });
        data += ordre;
        console.log(data.split('&'));
        $.post(window.location, data)
            .done(function (result) {
                window.location.replace('/collection-analyses');
            });
    });

    const fv = FormValidation.formValidation(
        document.getElementById('form_1'),
        {
            fields: {
                'nom': {
                    validators: {
                        notEmpty: {
                            message: 'Nom est obligatoire'
                        }
                    }
                }
            },

            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        }
    );

    fv.on('core.form.valid', function (event) {
        $('#btn-enregistrer').prop('disabled', true);
    });

});
