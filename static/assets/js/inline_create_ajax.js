import { loadItemList } from './utils/loadAjax.js';
import { showAlert } from './utils/alert.js';


// function loadCompanies() {
//     setInterval(function(){
//         $.ajax({
//             url: $('#list-container').data('url'),
//             type: 'GET',
//             dataType: 'json',
//             success: function(response) {
//                 let ListContainer = $('#list-container');
//                 let PaginationContainer = $('#pagination-container');
//                 let items = response.items;
//                 let pagination = response.pagination;
//                 let listHtml = '<div class="list-group">';
//                 items.forEach(function(item) {
//                     listHtml += '<a href="' + item.detail_url + '" class="list-group-item list-group-item-action">' + item.name + '</a>';
//                 });
//                 listHtml += '</div>';
//                 ListContainer.html(listHtml);

//                 // Handle pagination
//                 let paginationHtml = '';
//                 if (pagination.has_previous) {
//                     paginationHtml += '<li class="page-item"><a class="page-link" href="#" data-page="' + (pagination.current_page - 1) + '">Previous</a></li>';
//                 }
//                 for (let i = 1; i <= pagination.total_pages; i++) {
//                     let activeClass = (i === pagination.current_page) ? 'active' : '';
//                     paginationHtml += '<li class="page-item ' + activeClass + '"><a class="page-link" href="#" data-page="' + i + '">' + i + '</a></li>';
//                 }
//                 if (pagination.has_next) {
//                     paginationHtml += '<li class="page-item"><a class="page-link" href="#" data-page="' + (pagination.current_page + 1) + '">Next</a></li>';
//                 }
//                 PaginationContainer.html(paginationHtml);

//                 // Attach click event for pagination links
//                 $('.page-link').on('click', function(event) {
//                     event.preventDefault();
//                     let page = $(this).data('page');
//                     fetchCompanies(page);
//                 });
//             }
//         });
//     }, 5000);
// }

// function fetchCompanies(page) {
//     $.ajax({
//         url: $('#list-container').data('url') + '?page=' + page,
//         type: 'GET',
//         dataType: 'json',
//         success: function(response) {
//             let ListContainer = $('#list-container');
//             let PaginationContainer = $('#pagination-container');
//             let items = response.items;
//             let pagination = response.pagination;
//             let listHtml = '<div class="list-group">';
//             items.forEach(function(item) {
//                 listHtml += '<a href="' + item.detail_url + '" class="list-group-item list-group-item-action">' + item.name + '</a>';
//             });
//             listHtml += '</div>';
//             ListContainer.html(listHtml);

//             // Handle pagination
//             let paginationHtml = '';
//             if (pagination.has_previous) {
//                 paginationHtml += '<li class="page-item"><a class="page-link" href="#" data-page="' + (pagination.current_page - 1) + '">Previous</a></li>';
//             }
//             for (let i = 1; i <= pagination.total_pages; i++) {
//                 let activeClass = (i === pagination.current_page) ? 'active' : '';
//                 paginationHtml += '<li class="page-item ' + activeClass + '"><a class="page-link" href="#" data-page="' + i + '">' + i + '</a></li>';
//             }
//             if (pagination.has_next) {
//                 paginationHtml += '<li class="page-item"><a class="page-link" href="#" data-page="' + (pagination.current_page + 1) + '">Next</a></li>';
//             }
//             PaginationContainer.html(paginationHtml);

//             // Attach click event for pagination links
//             $('.page-link').on('click', function(event) {
//                 event.preventDefault();
//                 let page = $(this).data('page');
//                 fetchCompanies(page);
//             });
//         }
//     });
// }

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

    $(function() {
        let contactFormCount = "{{ contacts.total_form_count }}";
        let addressFormCount = "{{ addresses.total_form_count }}";
    
        function updateFormNumbers(formTemplate, formCount) {
            formTemplate.find('input, select, textarea').each(function() {
                const name = $(this).attr('name').replace(/-\d+-/, `-${formCount}-`);
                $(this).attr('name', name);
                const id = $(this).attr('id').replace(/-\d+-/, `-${formCount}-`);
                $(this).attr('id', id);
            });
            formTemplate.find('label').each(function() {
                const newFor = $(this).attr('for').replace(/-\d+-/, `-${formCount}-`);
                $(this).attr('for', newFor);
            });
        }
    
        $('#add-contact').click(function() {
            const formTemplate = $('#contacts-formset .form-group:first').clone();
            updateFormNumbers(formTemplate, contactFormCount);
            $('#contacts-formset').append(formTemplate);
            contactFormCount++;
        });
    
        $('#add-address').click(function() {
            const formTemplate = $('#addresses-formset .form-group:first').clone();
            updateFormNumbers(formTemplate, addressFormCount);
            $('#addresses-formset').append(formTemplate);
            addressFormCount++;
        });
    
        function handleFormSubmit(event, url, clearForm) {
            event.preventDefault();
            let validFormat=validateForm();
            if (validFormat){
                console.log('valid');
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: $('#create-form').serialize(),
                    dataType: 'json',
                    success: function(response) {
                        if (response.success) {
                            $('#alert').html('<div class="alert alert-success">Successfully submitted!</div>').show();
                            if (clearForm) {
                                $('#create-form')[0].reset();
                                $('#contacts-formset').find('.form-group:gt(0)').remove();
                                $('#addresses-formset').find('.form-group:gt(0)').remove();
                            } else {
                                window.location.href = response.redirect_url;
                            }
                        } else {
                            $('#alert').html('<div class="alert alert-danger">' + response.errors + '</div>').show();
                        }
                    }
                });
            }else {
                console.log('bad form inline')
            };
        }
    
        // function validateForm() {
        //     let isValid = true;
        //     $('#create-form .form-control').each(function() {
        //         if ($(this).prop('required') && $(this).val() === '') {
        //             isValid = false;
        //             $(this).addClass('is-invalid');
        //         } else {
        //             $(this).removeClass('is-invalid');
        //         }
        //     });
        //     return isValid;
        // }
    
        $('#add-another').on('click', function(event) {
            handleFormSubmit(event, window.location.href, true);
        });
    
        $('#submit-done').on('click', function(event) {
            handleFormSubmit(event, window.location.href, false);
        });
    
        setTimeout(function() {
            $('#alert').fadeOut('slow');
        }, 10000);
    
        $('#alert').on('click', '.close', function() {
            $(this).parent().fadeOut('slow');
        });
        // function loadCompanies() {
        //     setInterval(function(){
                
        //         $.ajax({
        //             url: $('#list-container').data('url'),
        //             type: 'GET',
        //             dataType: 'json',
        //             success: function(response) {
        //                 let ListContainer = $('#list-container');
        //                 let items = response.items;
        //                 let pagination = response.pagination;
        //                 let listHtml = '<div class="list-group">';
        //                 items.forEach(function(item) {
        //                     listHtml += '<a href="#" class="list-group-item list-group-item-action">' + item.name + '</a>';
        //                 });
        //                 listHtml += '</div>';
        //                 ListContainer.html(listHtml);
        //                 // Handle pagination here
        //             }
        //         });
        //     },5000 );
        // }
    
        loadItemList();
    });
})









