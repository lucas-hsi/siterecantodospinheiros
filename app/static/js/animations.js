/**
 * Recantos dos Pinheiros — Animations
 * AOS init, GSAP parallax hero, animated counters
 */

document.addEventListener('DOMContentLoaded', () => {
    initAOS();
    initParallaxHero();
    initCounters();
    initStaggerCards();
});

/* ─── AOS (Animate on Scroll) ───────────────────────────────── */
function initAOS() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 80,
            disable: 'mobile', // Desabilita em mobile para performance
        });
    }
}

/* ─── Parallax Hero (GSAP) ──────────────────────────────────── */
function initParallaxHero() {
    const heroBg = document.getElementById('heroBg');
    if (!heroBg || typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

    gsap.registerPlugin(ScrollTrigger);

    gsap.to(heroBg, {
        y: '20%',
        scale: 1.15,
        ease: 'none',
        scrollTrigger: {
            trigger: '#hero',
            start: 'top top',
            end: 'bottom top',
            scrub: 1,
        },
    });

    // Hero content fade out on scroll
    const heroContent = document.querySelector('.hero__content');
    if (heroContent) {
        gsap.to(heroContent, {
            y: -50,
            opacity: 0,
            ease: 'none',
            scrollTrigger: {
                trigger: '#hero',
                start: '30% top',
                end: '80% top',
                scrub: 1,
            },
        });
    }
}

/* ─── Animated Counters ─────────────────────────────────────── */
function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.counter, 10);
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }

        let display = Math.floor(current);
        if (target >= 1000) {
            display = Math.floor(current).toLocaleString('pt-BR');
        }

        // Adiciona o "+" para números grandes
        element.textContent = target >= 100 ? display + '+' : display;
    }, 16);
}

/* ─── Stagger Card Animations (GSAP) ───────────────────────── */
function initStaggerCards() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

    gsap.registerPlugin(ScrollTrigger);

    // Cards de destaques na home
    const cardSections = document.querySelectorAll('.grid');
    cardSections.forEach(section => {
        const cards = section.querySelectorAll('.card, .testimonial-card');
        if (cards.length === 0) return;

        gsap.fromTo(cards, 
            { y: 40, opacity: 0 },
            {
                y: 0,
                opacity: 1,
                stagger: 0.15,
                duration: 0.6,
                ease: 'power2.out',
                scrollTrigger: {
                    trigger: section,
                    start: 'top 80%',
                    once: true,
                },
            }
        );
    });
}
