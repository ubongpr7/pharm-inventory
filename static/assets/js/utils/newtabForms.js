function openAddItemTab(button) {
    const url = button.getAttribute('data-url');
    const field = button.getAttribute('data-field');
    const newTab = window.open(url, '_blank');

    const interval = setInterval(() => {
        if (newTab.closed) {
            clearInterval(interval);
            refreshFieldOptions(field);
        }
    }, 1000);
}

function refreshFieldOptions(field) {
    const url = document.querySelector(`[data-field="${field}"]`).getAttribute('data-url').replace('add/', 'list/');
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const fieldElement = document.querySelector(`[name="${field}"]`);
            fieldElement.innerHTML = '';
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item.name;
                fieldElement.appendChild(option);
            });
        });
}
