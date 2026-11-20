(function () {
    'use strict';

    const form = document.getElementById('adminLoginForm');
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');
    const usernameGroup = document.getElementById('usernameGroup');
    const passwordGroup = document.getElementById('passwordGroup');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const togglePasswordBtn = document.getElementById('togglePassword');

    if (togglePasswordBtn && passwordInput) {
        const iconEye = togglePasswordBtn.querySelector('.icon-eye');
        const iconEyeOff = togglePasswordBtn.querySelector('.icon-eye-off');

        togglePasswordBtn.addEventListener('click', function () {
            const isHidden = passwordInput.type === 'password';
            passwordInput.type = isHidden ? 'text' : 'password';
            togglePasswordBtn.setAttribute('aria-pressed', String(isHidden));
            togglePasswordBtn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
            togglePasswordBtn.setAttribute('title', isHidden ? 'Hide password' : 'Show password');

            if (iconEye && iconEyeOff) {
                iconEye.classList.toggle('hidden', isHidden);
                iconEyeOff.classList.toggle('hidden', !isHidden);
            }
        });
    }

    function setFieldError(group, errorEl, message) {
        if (!group || !errorEl) {
            return;
        }
        if (message) {
            group.classList.add('has-error');
            errorEl.textContent = message;
        } else {
            group.classList.remove('has-error');
            errorEl.textContent = '';
        }
    }

    if (usernameInput) {
        usernameInput.addEventListener('input', function () {
            if (usernameInput.value.trim()) {
                setFieldError(usernameGroup, usernameError, '');
            }
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            if (passwordInput.value) {
                setFieldError(passwordGroup, passwordError, '');
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function (event) {
            let isValid = true;

            if (usernameInput && !usernameInput.value.trim()) {
                setFieldError(usernameGroup, usernameError, 'Please enter your username.');
                isValid = false;
            } else {
                setFieldError(usernameGroup, usernameError, '');
            }

            if (passwordInput && !passwordInput.value) {
                setFieldError(passwordGroup, passwordError, 'Please enter your password.');
                isValid = false;
            } else {
                setFieldError(passwordGroup, passwordError, '');
            }

            if (!isValid) {
                event.preventDefault();
                if (usernameInput && !usernameInput.value.trim()) {
                    usernameInput.focus();
                } else if (passwordInput) {
                    passwordInput.focus();
                }
            }
        });
    }
})();
