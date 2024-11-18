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

const elements = document.querySelectorAll('a, button');

elements.forEach(element => {
    let isAnimating = false;

    element.addEventListener('click', event => {
        if (isAnimating || isFirefox) return;

        isAnimating = true;
        event.preventDefault();

        const targetUrl = element.href || element.getAttribute('data-url');
        const circle = document.createElement('div');
        circle.classList.add('circle');
        document.body.appendChild(circle);

        const clickX = event.clientX;
        const clickY = event.clientY;

        circle.style.left = `${clickX}px`;
        circle.style.top = `${clickY}px`;

        const maxDimension = Math.max(window.innerWidth, window.innerHeight) * 5;

        requestAnimationFrame(() => {
            circle.style.width = `${maxDimension}px`;
            circle.style.height = `${maxDimension}px`;

            setTimeout(() => {
                circle.style.backgroundColor = '#121212';
            }, 0);
        });

        setTimeout(() => {
            if (targetUrl) {
                window.location.href = targetUrl;
            } else {
                element.click();
            }

            isAnimating = false;
        }, 500);
    });
});

document.getElementById('backArrow').addEventListener('click', () => {
    removeCircles();
});
