
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('menu-toggle').addEventListener('click', function (e) {
        e.preventDefault();
        document.getElementById('wrapper').classList.toggle('toggled');
    });
    
    // Handle dropdown submenu
    document.querySelectorAll('.dropdown-submenu > a').forEach(function (element) {
        element.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const submenu = this.nextElementSibling;
            if (submenu) {
                submenu.classList.toggle('show');
            }
        });
    });

    document.addEventListener('click', function (e) {
        document.querySelectorAll('.dropdown-menu.show').forEach(function (menu) {
            if (!menu.contains(e.target)) {
                menu.classList.remove('show');
            }
        });
    });
});
