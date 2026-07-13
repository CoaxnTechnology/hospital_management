let specialites = [
    "MEDECINE GENERALE", "ANESTHESIOLOGIE - REANIMATION CHIRURGICALE", "PATHOLOGIE CARDIO-VASCULAIRE", "CHIRURGIE GENERALE", "DERMATOLOGIE ET VENEROLOGIE", "RADIODIAGNOSTIC ET IMAGERIE MEDICALE", "GYNECOLOGIE OBSTETRIQUE", "GASTRO-ENTEROLOGIE ET HEPATOLOGIE", "MEDECINE INTERNE", "NEUROCHIRURGIEN", "OTO RHINO LARYNGOLOGISTE", "PEDIATRE", "PNEUMOLOGIE", "RHUMATOLOGIE", "OPHTAMOLOGIE", "CHIRURGIE UROLOGIQUE", "NEURO PSYCHIATRIE", "STOMATOLOGIE", "CHIRURGIE DENTAIRE", "SAGE FEMME", "INFIRMIER", "MASSEUR KINESITHERAPEUTE", "PEDICURE", "ORTHOPHONISTE", "ORTHOPTISTE", "LABORATOIRE D'ANALYSES MEDICALES", "MEDECINE PHYSIQUE ET DE READAPTATION", "NEUROLOGIE", "PSYCHIATRIE GENERALE", "NEPHROLOGIE", "CHIRURGIE DENTAIRE (Spéc. O.D.F.)", "ANATOMIE-CYTOLOGIE-PATHOLOGIQUES", "MEDECIN BIOLOGISTE", "LABORATOIRE POLYVALENT", "LABORATOIRE ANATOMO-PATHOLOGISTE", "CHIRURGIE ORTHOPEDIQUE et TRAUMATOLOGIE", "ENDOCRINOLOGIE et METABOLISMES", "CHIRURGIE INFANTILE", "CHIRURGIE MAXILLO-FACIALE", "CHIRURGIE MAXILLO-FACIALE ET STOMATOLOGIE", "CHIRURGIE PLASTIQUE RECONSTRUCTRICE ET ESTHECS", "CHIRURGIE THORACIQUE ET CARDIO-VASCULAIRE", "CHIRURGIE VASCULAIRE", "CHIRURGIE VISCERALE ET DIGESTIVE", "PHARMACIEN", "GYNECOLOGIE MEDICALE", "HEMATOLOGIE", "MEDECINE NUCLEAIRE", "ONCOLOGIE MEDICALE", "ONCOLOGIE RADIOTHERAPIQUE", "PSYCHIATRIE DE L'ENFANT ET DE L'ADOLESCENT", "RADIOTHERAPIE", "OBSTETRIQUE", "SANTE PUBLIQUE ET MEDECINE SOCIALE", "AUTRE"
];

$(document).ready(() => {

    $('#id_email').inputmask({
        mask: "*{1,20}[.*{1,20}][.*{1,20}][.*{1,20}]@*{1,20}[.*{2,6}][.*{1,2}]",
        greedy: false,
        onBeforePaste: function (pastedValue, opts) {
            pastedValue = pastedValue.toLowerCase();
            return pastedValue.replace("mailto:", "");
        },
        definitions: {
            '*': {
                validator: "[0-9A-Za-z!#$%&'*+/=?^_`{|}~\-]",
                cardinality: 1,
                casing: "lower"
            }
        }
    });


    var liste_specialite = new Bloodhound({
        local: specialites,
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });


    $('#specialite').typeahead(null, {
        source: liste_specialite,
        name: 'specialites',
        minLength: 2,
    });

    FormValidation.formValidation(
        document.getElementById('form_praticien'),
        {
            fields: {
                'prenom': {
                    validators: {
                        notEmpty: {
                            message: 'Prénom est obligatoire'
                        }
                    }
                },

                'nom': {
                    validators: {
                        notEmpty: {
                            message: 'Nom est obligatoire'
                        }
                    }
                },

                'specialite': {
                    validators: {
                        notEmpty: {
                            message: 'Spécialité est obligatoire'
                        }
                    }
                },

                'email': {
                    validators: {
                        emailAddress: {
                            message: 'Email non valide'
                        }
                    }
                },

                'telephone': {
                    validators: {
                        numeric: {
                            message: 'Téléphone doit contenir des chiffres uniquement'
                        },
                        stringLength: {
                            min: 8,
                            max: 8,
                            message: 'Téléphone doit contenir 8 chiffres'
                        }
                    }
                },

            },
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                // Submit the form when all fields are valid
                defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
            }
        });

});


