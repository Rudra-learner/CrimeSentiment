document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMsg = document.getElementById('error-message');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const loginBtn = document.getElementById('login-btn');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = usernameInput.value;
        const password = passwordInput.value;
        
        // Reset state
        errorMsg.textContent = '';
        errorMsg.classList.remove('show');
        loginBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'block';
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            if (response.ok) {
                // Success - redirect to dashboard
                localStorage.setItem('lastActivityTime', Date.now().toString());
                window.location.href = '/dashboard/';
            } else {
                // Failure
                const data = await response.json();
                errorMsg.textContent = data.message || 'Authentication failed. Access denied.';
                errorMsg.classList.add('show');
                
                // Add a subtle shake animation to the form
                const card = document.querySelector('.login-card');
                card.style.transform = 'translateX(-10px)';
                setTimeout(() => card.style.transform = 'translateX(10px)', 100);
                setTimeout(() => card.style.transform = 'translateX(-10px)', 200);
                setTimeout(() => card.style.transform = 'translateX(10px)', 300);
                setTimeout(() => card.style.transform = 'translateX(0)', 400);
            }
        } catch (error) {
            errorMsg.textContent = 'Connection error. Please try again later.';
            errorMsg.classList.add('show');
        } finally {
            loginBtn.disabled = false;
            btnText.style.display = 'inline-block';
            btnSpinner.style.display = 'none';
        }
    });
});
