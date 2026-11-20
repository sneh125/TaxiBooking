(function () {
    'use strict';

    const form = document.getElementById('adminRegisterForm');
    const fullNameInput = document.getElementById('id_full_name');
    const usernameInput = document.getElementById('id_username');
    const emailInput = document.getElementById('id_email');
    const passwordInput = document.getElementById('id_password');
    const confirmPasswordInput = document.getElementById('id_confirm_password');

    const groups = {
        fullName: { input: fullNameInput, group: document.getElementById('fullNameGroup'), error: document.getElementById('fullNameError') },
        username: { input: usernameInput, group: document.getElementById('usernameGroup'), error: document.getElementById('usernameError') },
        email: { input: emailInput, group: document.getElementById('emailGroup'), error: document.getElementById('emailError') },
        password: { input: passwordInput, group: document.getElementById('passwordGroup'), error: document.getElementById('passwordError') },
        confirmPassword: { input: confirmPasswordInput, group: document.getElementById('confirmPasswordGroup'), error: document.getElementById('confirmPasswordError') },
    };

    document.querySelectorAll('.password-toggle[data-toggle-target]').forEach(function (btn) {
        const targetId = btn.getAttribute('data-toggle-target');
        const targetInput = document.getElementById(targetId);
        if (!targetInput) {
            return;
        }
        const iconEye = btn.querySelector('.icon-eye');
        const iconEyeOff = btn.querySelector('.icon-eye-off');

        btn.addEventListener('click', function () {
            const isHidden = targetInput.type === 'password';
            targetInput.type = isHidden ? 'text' : 'password';
            btn.setAttribute('aria-pressed', String(isHidden));
            btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
            btn.setAttribute('title', isHidden ? 'Hide password' : 'Show password');

            if (iconEye && iconEyeOff) {
                iconEye.classList.toggle('hidden', isHidden);
                iconEyeOff.classList.toggle('hidden', !isHidden);
            }
        });
    });

    function setFieldError(entry, message) {
        if (!entry || !entry.group || !entry.error) {
            return;
        }
        if (message) {
            entry.group.classList.add('has-error');
            entry.error.textContent = message;
        } else {
            entry.group.classList.remove('has-error');
            entry.error.textContent = '';
        }
    }

    Object.values(groups).forEach(function (entry) {
        if (entry.input) {
            entry.input.addEventListener('input', function () {
                if (entry.input.value.trim()) {
                    setFieldError(entry, '');
                }
            });
        }
    });

    if (form) {
        form.addEventListener('submit', function (event) {
            let firstInvalid = null;

            function fail(entry, message) {
                setFieldError(entry, message);
                if (!firstInvalid && entry.input) {
                    firstInvalid = entry.input;
                }
            }

            if (fullNameInput && !fullNameInput.value.trim()) {
                fail(groups.fullName, 'Please enter your full name.');
            } else {
                setFieldError(groups.fullName, '');
            }

            if (usernameInput && !usernameInput.value.trim()) {
                fail(groups.username, 'Please choose a username.');
            } else {
                setFieldError(groups.username, '');
            }

            const emailVal = emailInput ? emailInput.value.trim() : '';
            if (!emailVal) {
                fail(groups.email, 'Please enter your email address.');
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
                fail(groups.email, 'Please enter a valid email address.');
            } else {
                setFieldError(groups.email, '');
            }

            const passwordVal = passwordInput ? passwordInput.value : '';
            if (!passwordVal) {
                fail(groups.password, 'Please enter a password.');
            } else {
                setFieldError(groups.password, '');
            }

            const confirmVal = confirmPasswordInput ? confirmPasswordInput.value : '';
            if (!confirmVal) {
                fail(groups.confirmPassword, 'Please confirm your password.');
            } else if (passwordVal && passwordVal !== confirmVal) {
                fail(groups.confirmPassword, 'Passwords do not match.');
            } else {
                setFieldError(groups.confirmPassword, '');
            }

            if (firstInvalid) {
                event.preventDefault();
                firstInvalid.focus();
            }
        });
    }
})();
