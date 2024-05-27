$(document).ready(function() {
    $('#add-category').on('click', function() {
        $('#categoryModal').modal('show');
    });

    $('#save-category').on('click', function() {
        $.ajax({
            url: '{% url "category_create" %}',  // URL for creating category
            type: 'POST',
            data: $('#category-form').serialize(),
            success: function(response) {
                if (response.success) {
                    // Update the original form field
                    let newOption = new Option(response.category.name, response.category.id, true, true);
                    $('#id_category').append(newOption).trigger('change');
                    $('#categoryModal').modal('hide');
                } else {
                    // Handle form errors
                }
            }
        });
    });
});




// static/js/add_entry.js

$(document).ready(function() {
    // Open the popup form when the add button is clicked
    $('.add-entry').on('click', function() {
        let fieldName = $(this).data('field-name');
        $('#popupModal').data('field-name', fieldName).modal('show');
    });

    // Handle the form submission inside the popup
    $('#popupForm').on('submit', function(event) {
        event.preventDefault();
        let fieldName = $('#popupModal').data('field-name');
        let formData = $(this).serialize();

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            success: function(response) {
                // Update the field with the new entry
                if (response.success) {
                    let newOption = new Option(response.name, response.id, true, true);
                    $(`select[name=${fieldName}]`).append(newOption).trigger('change');
                    $('#popupModal').modal('hide');
                } else {
                    // Handle validation errors
                    $('#popupModal .modal-body').html(response.form_html);
                }
            }
        });
    });
});




// static/js/add_entry.js

$(document).ready(function() {
    // Open the popup form when the add button is clicked
    $('.add-entry').on('click', function() {
        let fieldName = $(this).data('field-name');
        let url = $(this).data('url');
        
        $.ajax({
            url: url,
            type: 'GET',
            success: function(response) {
                $('#popupModal .modal-body').html(response.form_html);
                $('#popupModal').data('field-name', fieldName).modal('show');
            }
        });
    });

    // Handle the form submission inside the popup
    $('#popupForm').on('submit', function(event) {
        event.preventDefault();
        let fieldName = $('#popupModal').data('field-name');
        let formData = $(this).serialize();

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    let newOption = new Option(response.name, response.id, true, true);
                    $(`select[name=${fieldName}]`).append(newOption).trigger('change');
                    $('#popupModal').modal('hide');
                } else {
                    $('#popupModal .modal-body').html(response.form_html);
                }
            }
        });
    });
});
