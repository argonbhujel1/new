document.addEventListener('DOMContentLoaded', function() {
    // Cookie consent
    if (!localStorage.getItem('cookieAccepted')) {
        const el = document.getElementById('cookieConsent');
        if (el) el.style.display = 'block';
    }
    
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });
    
    // Lazy load images
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });
        document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
    }
});

function acceptCookies() {
    localStorage.setItem('cookieAccepted', '1');
    const el = document.getElementById('cookieConsent');
    if (el) el.style.display = 'none';
}
