/**
 * AuthGuard Authentication & Session Controller
 */

const SESSION_KEY = 'authguard_active_user';
const FLASH_KEY = 'authguard_flash_message';

// Set flash message for display after page redirect
function setFlashMessage(message, type = 'success') {
    sessionStorage.setItem(FLASH_KEY, JSON.stringify({ message, type }));
}

// Display stored flash message if one exists
function renderFlashMessage() {
    const flashData = sessionStorage.getItem(FLASH_KEY);
    if (flashData) {
        sessionStorage.removeItem(FLASH_KEY);
        try {
            const { message, type } = JSON.parse(flashData);
            showAlert(message, type);
        } catch (e) {
            console.error('Error parsing flash message', e);
        }
    }
}

// Show alert banner on page
function showAlert(message, type = 'danger') {
    const container = document.getElementById('alertContainer');
    if (!container) return;

    const iconClass = type === 'success' 
        ? 'fa-solid fa-circle-check'
        : type === 'warning'
        ? 'fa-solid fa-circle-exclamation'
        : type === 'info'
        ? 'fa-solid fa-circle-info'
        : 'fa-solid fa-triangle-exclamation';

    container.innerHTML = `
        <div class="alert alert-${type} fade-in">
            <i class="alert-icon ${iconClass}"></i>
            <span>${message}</span>
            <button type="button" class="alert-close" onclick="this.parentElement.remove();">&times;</button>
        </div>
    `;
}

// Get currently authenticated session user
function getSessionUser() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

// Set active session
function setSessionUser(user) {
    const safeUser = {
        id: user.id,
        fullName: user.fullName,
        email: user.email,
        createdAt: user.createdAt
    };
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(safeUser));
}

// Guard: Require login for protected pages (Dashboard)
function requireAuth() {
    const user = getSessionUser();
    if (!user) {
        setFlashMessage('Please log in to access this page.', 'warning');
        window.location.replace('login.html');
        return false;
    }
    return user;
}

// Guard: Redirect already logged-in users away from login/register
function redirectIfLoggedIn() {
    const user = getSessionUser();
    if (user) {
        window.location.replace('dashboard.html');
    }
}

// End user session
function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    setFlashMessage('You have been logged out successfully.', 'info');
    window.location.replace('login.html');
}

// Toggle password visibility
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (!input) return;

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

// Live password match feedback
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

// Dynamic password strength meter
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

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
    renderFlashMessage();
});
