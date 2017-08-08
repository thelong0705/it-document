$(document).ready(function () {
    let formInputs = $('input[type="text"],input[type="password"],input[type="email"]');
    let check = formInputs.data('ui-autocomplete') !== undefined;
    if (check) {
        formInputs.parent().children('p.formLabel',).addClass('formTop');
        $('div#formWrapper').addClass('darken-bg');
        $('div.logo').addClass('logo-active');
    }

    formInputs.focus(function () {
        $(this).parent().children('p.formLabel').addClass('formTop');
        $('div#formWrapper').addClass('darken-bg');
        $('div.logo').addClass('logo-active');
    });
    formInputs.focusout(function () {
        if ($.trim($(this).val()).length == 0) {
            $(this).parent().children('p.formLabel').removeClass('formTop');
        }
        $('div#formWrapper').removeClass('darken-bg');
        $('div.logo').removeClass('logo-active');
    });
    $('p.formLabel').click(function () {
        $(this).parent().children('.form-style').focus();
    });
});