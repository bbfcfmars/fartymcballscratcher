// Subtle mouse trail effect
document.addEventListener('mousemove', (e) => {
    const trail = document.createElement('div');
    trail.className = 'mouse-trail';
    trail.style.left = e.pageX + 'px';
    trail.style.top = e.pageY + 'px';
    document.body.appendChild(trail);

    setTimeout(() => {
        trail.remove();
    }, 1000);
});

// Add parallax effect to images
document.addEventListener('mousemove', (e) => {
    const images = document.querySelectorAll('img');
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;

    images.forEach(img => {
        const speed = 0.1;
        const x = (mouseX - 0.5) * speed * 100;
        const y = (mouseY - 0.5) * speed * 100;
        img.style.transform = `translate(${x}px, ${y}px)`;
    });
});

// Add glow effect to headings on scroll
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.textShadow = '0 0 10px rgba(0, 255, 157, 0.8), 0 0 20px rgba(0, 255, 157, 0.5), 0 0 30px rgba(0, 255, 157, 0.3)';
            setTimeout(() => {
                entry.target.style.textShadow = '0 0 5px rgba(0, 255, 157, 0.5), 0 0 10px rgba(0, 255, 157, 0.3), 0 0 15px rgba(0, 255, 157, 0.2)';
            }, 1000);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('h1, h2, h3').forEach(heading => {
    observer.observe(heading);
}); 