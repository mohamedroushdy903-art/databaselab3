/**
 * AuthGuard Client-Side Interactions & Form Validations
 */

// Toggle Password Visibility (Eye Icon)
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Check if Password and Confirm Password match in real time
function checkPasswordMatch() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const matchHint = document.getElementById('matchHint');

    if (!confirmPassword || !matchHint) return;

    if (confirmPassword.value === '') {
        matchHint.textContent = '';
        matchHint.className = 'form-hint match-hint';
        return;
    }

    if (password.value === confirmPassword.value) {
        matchHint.textContent = '✓ Passwords match';
        matchHint.className = 'form-hint match-hint valid';
    } else {
        matchHint.textContent = '✗ Passwords do not match';
        matchHint.className = 'form-hint match-hint invalid';
    }
}

// Dynamic Password Strength Meter
function updatePasswordStrength() {
    const password = document.getElementById('password');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');

    if (!password || !strengthBar || !strengthText) return;

    const val = password.value;
    if (val.length === 0) {
        strengthBar.className = 'strength-bar';
        strengthText.textContent = 'Password must be at least 6 characters';
        return;
    }

    let score = 0;
    if (val.length >= 6) score += 1;
    if (val.length >= 10) score += 1;
    if (/[A-Z]/.test(val)) score += 1;
    if (/[0-9]/.test(val)) score += 1;
    if (/[^A-Za-z0-9]/.test(val)) score += 1;

    if (score <= 2) {
        strengthBar.className = 'strength-bar weak';
        strengthText.textContent = 'Weak password';
    } else if (score <= 4) {
        strengthBar.className = 'strength-bar medium';
        strengthText.textContent = 'Medium password strength';
    } else {
        strengthBar.className = 'strength-bar strong';
        strengthText.textContent = 'Strong password';
    }
}

// Client-Side Registration Form Submission Guard
function validateRegistrationForm() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match. Please ensure both password fields match.');
        return false;
    }

    if (password.length < 6) {
        alert('Password must be at least 6 characters long.');
        return false;
    }

    return true;
}
