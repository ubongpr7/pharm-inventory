let currentPage = 1;
let intervalId;

export  function loadItemList(page = 1, initialLoad = false) {
    console.log('loadAjax is working')
    if (!initialLoad && intervalId) {
        clearInterval(intervalId);
    }
    currentPage = page;
    $.ajax({
        url: $('#list-container').data('url'),
        type: 'GET',
        data: { page: currentPage },
        dataType: 'json',
        success: function(response) {
            let inventoryListContainer = $('#list-container');
            let paginationContainer = $('#pagination-container');
            let items = response.items;
            let pagination = response.pagination;

            // Update the list items
            let listHtml = '<div class="list-group">';
            items.forEach(function(item) {
                listHtml += '<a href="' + item.detail_url + '" class="list-group-item list-group-item-action">' + item.name + '</a>';
            });
            listHtml += '</div>';
            inventoryListContainer.html(listHtml);

            // Update the pagination controls
            let paginationHtml = '';
            if (pagination.has_previous) {
                paginationHtml += '<li class="page-item"><a class="page-link" href="#" data-page="' + (pagination.current_page - 1) + '">Previous</a></li>';
            }
            for (let i = 1; i <= pagination.total_pages; i++) {
                let activeClass = (i === pagination.current_page) ? 'active' : '';
                paginationHtml += '<li class="page-item ' + activeClass + '"><a class="page-link" href="#" data-page="' + i + '">' + i + '</a></li>';
            }
            if (pagination.has_next) {
                paginationHtml += '<li class="page-item"><a class="page-link" href="#" data-page="' + (pagination.current_page + 1) + '">Next</a></li>';
            }
            paginationContainer.html(paginationHtml);

            // Attach click event for pagination links
            $('.page-link').on('click', function(event) {
                event.preventDefault();
                let page = $(this).data('page');
                loadItemList(page);
            });
        }
    });

    if (!initialLoad) {
        intervalId = setInterval(function () {
            loadItemList(currentPage, true);
        }, 5000);
    }
}