jQuery(document).ready(function () {

    const autocomplete = function (key) {
        return new Bloodhound({
            local: codes_postaux,
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace(key),
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });
    };

    let ancien_cp = '';
    $('[name="cp"]').typeahead(null, {
        name: 'codes_postaux',
        display: 'code',
        source: autocomplete('code'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><strong><%=code%></strong> – <%=ville%> - <%=gouvernorat%></div>')
        }
    }).on('typeahead:select', (e, suggestion) => {
        $('[name="gouvernorat"]').typeahead('val', suggestion.gouvernorat);
        $('[name="ville"]').typeahead('val', suggestion.ville);
        $('[name="pays"]').val(suggestion.pays);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        $('[name="gouvernorat"]').typeahead('val', suggestion.gouvernorat);
        $('[name="ville"]').typeahead('val', suggestion.ville);
        $('[name="pays"]').val(suggestion.pays);
    });

    $('[name="ville"]').typeahead(null, {
        name: 'codes_postaux',
        display: 'ville',
        source: autocomplete('ville'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><%=code%> – <strong><%=ville%></strong> - <%=gouvernorat%></div>')
        }
    }).on('typeahead:select', (e, suggestion) => {
        $('[name="cp"]').typeahead('val', suggestion.code);
        $('[name="gouvernorat"]').typeahead('val', suggestion.gouvernorat);
        $('[name="pays"]').val(suggestion.pays);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        $('[name="cp"]').typeahead('val', suggestion.code);
        $('[name="gouvernorat"]').typeahead('val', suggestion.gouvernorat);
        $('[name="pays"]').val(suggestion.pays);
    });

    $('[name="gouvernorat"]').typeahead(null, {
        name: 'codes_postaux',
        display: 'gouvernorat',
        source: autocomplete('gouvernorat'),
        minLength: 2,
        templates: {
            suggestion: _.template('<div><%=code%> – <%=ville%> - <strong><%=gouvernorat%></strong></div>')
        }
    }).on('typeahead:select', (e, suggestion) => {
        $('[name="cp"]').typeahead('val', suggestion.code);
        $('[name="ville"]').typeahead('val', suggestion.ville);
        $('[name="pays"]').val(suggestion.pays);
    }).on('typeahead:autocomplete', (e, suggestion) => {
        $('[name="cp"]').typeahead('val', suggestion.code);
        $('[name="ville"]').typeahead('val', suggestion.ville);
        $('[name="pays"]').val(suggestion.pays);
    });
});