(function () {
    'use strict';

    function toggleInputVisibility(button, input) {
        if (!button || !input) {
            return;
        }
        const isHidden = input.type === 'password';
        input.type = isHidden ? 'text' : 'password';
        button.setAttribute('aria-pressed', String(isHidden));
        button.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
        button.setAttribute('title', isHidden ? 'Hide password' : 'Show password');

        const eyeShow = button.querySelector('.icon-eye');
        const eyeHide = button.querySelector('.icon-eye-off');
        if (eyeShow && eyeHide) {
            eyeShow.classList.toggle('hidden', isHidden);
            eyeHide.classList.toggle('hidden', !isHidden);
        }
    }

    document.querySelectorAll('[data-toggle-password]').forEach(function (button) {
        const targetId = button.getAttribute('data-toggle-password');
        const targetInput = document.getElementById(targetId);
        if (!targetInput) {
            return;
        }
        button.addEventListener('click', function () {
            toggleInputVisibility(button, targetInput);
        });
    });

    const deleteModal = document.getElementById('confirmDeleteModal');
    const deleteForm = document.getElementById('confirmDeleteForm');
    const deleteMessage = document.getElementById('confirmDeleteMessage');

    if (deleteModal && deleteForm && deleteMessage) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) {
                return;
            }
            const url = trigger.getAttribute('data-delete-url') || '';
            const label = trigger.getAttribute('data-delete-label') || 'this record';
            deleteForm.action = url;
            deleteMessage.textContent = 'Are you sure you want to delete ' + label + '? This action cannot be undone.';
        });
    }
})();
