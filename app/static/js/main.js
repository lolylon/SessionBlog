document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('show');
        }, 100 * index);
    });

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот пост? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    });

    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.querySelector('.image-preview');
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 70,
                behavior: 'smooth'
            });
        }
    });
});