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
    // document.body.style.opacity = '1';

    const overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.top = 0;
    overlay.style.bottom = 0;
    overlay.style.left = 0;
    overlay.style.right = 0;

    overlay.style.zIndex = 9999;
    overlay.style.backgroundColor = 'white';
    overlay.style.opacity = 1;
    overlay.style.transition = '1s ease-out opacity';

    overlay.style.pointerEvents = 'none';

    document.body.appendChild(overlay);

    requestAnimationFrame(() => {
        overlay.style.opacity = 0;
    });

    overlay.addEventListener('transitioned', () => {
        overlay.remove();
    });
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
                circle.style.backgroundColor = 'white';
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