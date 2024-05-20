function loadPage(pageName) {
    // Load content from the specified page
    const pages = ['home', 'inventory', 'add_inventory', 'notifications', 'patient_folder'];
    if (pages.includes(pageName)) {
        fetch(`${pageName}.html`)
            .then(response => response.text())
            .then(html => {
                document.querySelector('.w-4/5').innerHTML = html;
            })
            .catch(error => console.error('Error fetching page:', error));
    } else {
        console.error('Invalid page name');
    }
}

function togglePage(pageName) {
    // Toggle active class for sidebar buttons
    const buttons = document.querySelectorAll('.sidebar-button');
    buttons.forEach(button => {
        button.classList.remove('text-blue-300');
    });

    const activeButton = document.querySelector(`#${pageName}Button`);
    activeButton.classList.add('text-blue-300');

    // Load the selected page
    loadPage(pageName);
}

// Initial page load
loadPage('home');

