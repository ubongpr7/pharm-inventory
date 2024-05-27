import { loadItemList } from './utils/loadAjax.js';
import { showAlert } from './utils/alert.js';
// import { validateForm } from './inline_create_ajax.js';

function validateForm() {
    let isValid = true;
    $('#create-form .form-control').each(function() {
        if ($(this).prop('required') && $(this).val() === '') {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    return isValid;
}
$(document).ready(function() {
    $('#create-form').on('submit', function(event) {
        event.preventDefault();
        let action = $(document.activeElement).val();
        let ajaxUrl = $('#create-form').data('url');
        let formData = $(this).serialize() + '&action=' + action;
        if (validateForm()){

            $.ajax({
                url: ajaxUrl,
                type: 'POST',
                data: formData,
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        if (action === 'add_another') {
                            $('#create-form')[0].reset();
                            showAlert('Item added. You can add another.', 'success');
                            // loadItemList();
                        } else if (action === 'done') {
                            showAlert('Item added successfully.', 'success');
                            $('#create-form')[0].reset();
                            window.location.href = response.redirect_url;
                        }
                    } else {
                        showAlert('Error adding item.', 'danger');
                    }
                }
            });
        }else{
            console.log('bad form, create')
        };
    });

    // function showAlert(message, type) {
    //     let alertBox = $('#alert');
    //     let alertMessage = $('#alert-message');
    //     alertMessage.html(message);
    //     alertBox.removeClass('alert-success alert-danger').addClass('alert-' + type).show();
    //     setTimeout(function() {
    //         if (alertBox.is(':visible')) {
    //             alertBox.alert('close');
    //         }
    //     }, 10000);
    // }

    
    loadItemList();
});

