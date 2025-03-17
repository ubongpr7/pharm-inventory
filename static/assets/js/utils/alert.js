
export function showAlert(message, type) {
    let alertBox = $('#alert');
    let alertMessage = $('#alert-message');
    alertMessage.html(message);
    alertBox.removeClass('alert-success alert-danger').addClass('alert-' + type).show();
    setTimeout(function() {
        if (alertBox.is(':visible')) {
            alertBox.alert('close');
        }
    }, 10000);
}