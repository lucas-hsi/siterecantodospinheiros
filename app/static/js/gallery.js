/**
 * Recantos dos Pinheiros — Gallery
 * Filtro por categoria para galeria masonry
 */

document.addEventListener('DOMContentLoaded', () => {
    const galleryGrid = document.getElementById('galleryGrid');
    if (!galleryGrid) return;

    const tabs = document.querySelectorAll('.filter-tab');
    const items = galleryGrid.querySelectorAll('.masonry-item');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const filter = tab.dataset.filter;

            // Ativar tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Filtrar items com animação
            items.forEach((item, index) => {
                if (filter === 'all' || item.dataset.category === filter) {
                    item.style.display = '';
                    item.style.animation = `fadeInUp 0.4s ease ${index * 0.05}s forwards`;
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});
