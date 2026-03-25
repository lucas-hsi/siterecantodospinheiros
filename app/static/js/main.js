/**
 * Recantos dos Pinheiros — Main JavaScript
 * Navbar scroll effect, hamburger menu, smooth scroll
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initSmoothScroll();
    initAccordion();
});

/* ─── Navbar ────────────────────────────────────────────────── */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');

    // Scroll effect
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    }, { passive: true });

    // Hamburger toggle
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });

        // Close menu on link click
        navMenu.querySelectorAll('.navbar__link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Close menu on outside click
        document.addEventListener('click', (e) => {
            if (navMenu.classList.contains('active') &&
                !navMenu.contains(e.target) &&
                !hamburger.contains(e.target)) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
}

/* ─── Smooth Scroll ─────────────────────────────────────────── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = 80; // navbar height
                const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        });
    });
}

/* ─── Accordion (FAQ) ───────────────────────────────────────── */
function initAccordion() {
    document.querySelectorAll('.accordion__header').forEach(header => {
        header.addEventListener('click', () => {
            const item = header.parentElement;
            const body = item.querySelector('.accordion__body');
            const isActive = item.classList.contains('active');

            // Close all
            item.closest('.accordion').querySelectorAll('.accordion__item').forEach(i => {
                i.classList.remove('active');
                i.querySelector('.accordion__body').style.maxHeight = null;
            });

            // Toggle current
            if (!isActive) {
                item.classList.add('active');
                body.style.maxHeight = body.scrollHeight + 'px';
            }
        });
    });
}

/* ─── Toast Notification ────────────────────────────────────── */
function showToast(message, type = 'success', duration = 4000) {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast toast--${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

/* ─── Lightbox (Global) ─────────────────────────────────────── */
(function initLightbox() {
    const lightbox = document.getElementById('lightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    const lightboxClose = document.getElementById('lightboxClose');
    const lightboxPrev = document.getElementById('lightboxPrev');
    const lightboxNext = document.getElementById('lightboxNext');

    if (!lightbox) return;

    let currentImages = [];
    let currentIndex = 0;

    // Open lightbox from any element with data-lightbox
    document.addEventListener('click', (e) => {
        const trigger = e.target.closest('[data-lightbox]');
        if (!trigger) return;

        const src = trigger.dataset.lightbox;
        const allTriggers = Array.from(document.querySelectorAll('[data-lightbox]'));
        const visibleTriggers = allTriggers.filter(t => t.offsetParent !== null);

        currentImages = visibleTriggers.map(t => t.dataset.lightbox);
        currentIndex = currentImages.indexOf(src);
        if (currentIndex === -1) currentIndex = 0;

        lightboxImage.src = currentImages[currentIndex];
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    // Close
    lightboxClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });

    // Nav
    lightboxPrev.addEventListener('click', (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
        lightboxImage.src = currentImages[currentIndex];
    });

    lightboxNext.addEventListener('click', (e) => {
        e.stopPropagation();
        currentIndex = (currentIndex + 1) % currentImages.length;
        lightboxImage.src = currentImages[currentIndex];
    });

    // Keyboard
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') lightboxPrev.click();
        if (e.key === 'ArrowRight') lightboxNext.click();
    });

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
})();
