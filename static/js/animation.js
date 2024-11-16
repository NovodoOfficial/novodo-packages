const removeCircles = () => {
    const circles = document.querySelectorAll('.circle');
    circles.forEach(circle => {
        circle.remove();
    });
};

removeCircles();

const isFirefox = typeof InstallTrigger !== 'undefined';

window.addEventListener('load', () => {
    removeCircles();
    document.body.style.opacity = '1';
});

const links = document.querySelectorAll('a');

links.forEach(link => {
    link.addEventListener('click', event => {
        if (isFirefox) return;

        event.preventDefault();

        const targetUrl = link.href;
        const circle = document.createElement('div');
        circle.classList.add('circle');
        document.body.appendChild(circle);

        const clickX = event.clientX;
        const clickY = event.clientY;

        circle.style.left = `${clickX}px`;
        circle.style.top = `${clickY}px`;

        const maxDimension = Math.max(window.innerWidth, window.innerHeight) * 2;

        requestAnimationFrame(() => {
            circle.style.width = `${maxDimension}px`;
            circle.style.height = `${maxDimension}px`;

            setTimeout(() => {
                circle.style.backgroundColor = '#121212';
            }, 0);
        });

        setTimeout(() => {
            window.location.href = targetUrl;
        }, 500);
    });
});

document.getElementById('backArrow').addEventListener('click', () => {
    removeCircles();
});
