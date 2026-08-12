(function() {
    // 15 minutes of inactivity timeout
    const INACTIVITY_TIMEOUT = 15 * 60 * 1000; 

    function resetTimer() {
        localStorage.setItem('lastActivityTime', Date.now().toString());
    }

    function checkTimeout() {
        const lastActivity = localStorage.getItem('lastActivityTime');
        if (lastActivity) {
            const timeSinceLastActivity = Date.now() - parseInt(lastActivity, 10);
            if (timeSinceLastActivity > INACTIVITY_TIMEOUT) {
                // Time has expired, log out
                logoutUser();
            }
        } else {
            resetTimer();
        }
    }

    function logoutUser() {
        localStorage.removeItem('lastActivityTime');
        // Call the server logout endpoint, then redirect
        fetch('/api/logout', { method: 'POST' }).catch(() => {}).finally(() => {
            window.location.href = '/dashboard/login.html';
        });
    }

    // Check timeout on load
    checkTimeout();

    // Reset timer on user interactions
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    events.forEach(name => {
        document.addEventListener(name, resetTimer, true);
    });

    // Check periodically in case tab is left open and unused
    setInterval(checkTimeout, 60000); // Check every minute
})();
