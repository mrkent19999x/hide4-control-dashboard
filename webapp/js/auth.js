// auth.js - Simple Authentication Module for Hide4 Control Dashboard

class SimpleAuth {
    constructor() {
        this.username = 'admin';
        this.password = 'Hide4Admin2024!';
        this.sessionKey = 'hide4_admin_session';
        this.sessionTimeout = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
        this.isAuthenticated = false;
        
        this.init();
    }

    init() {
        // Check if user is already logged in
        this.checkExistingSession();
    }

    checkExistingSession() {
        const sessionData = localStorage.getItem(this.sessionKey);
        if (sessionData) {
            try {
                const session = JSON.parse(sessionData);
                const now = new Date().getTime();
                
                // Check if session is still valid
                if (now - session.timestamp < this.sessionTimeout) {
                    this.isAuthenticated = true;
                    console.log('✅ Existing session found - user authenticated');
                    return true;
                } else {
                    // Session expired
                    this.logout();
                    console.log('⚠️ Session expired - user logged out');
                }
            } catch (error) {
                console.error('❌ Error parsing session data:', error);
                this.logout();
            }
        }
        return false;
    }

    login(username, password) {
        console.log('🔐 Attempting login...');
        
        if (username === this.username && password === this.password) {
            // Create session
            const sessionData = {
                username: username,
                timestamp: new Date().getTime(),
                loginTime: new Date().toISOString()
            };
            
            localStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
            this.isAuthenticated = true;
            
            console.log('✅ Login successful');
            return true;
        } else {
            console.log('❌ Login failed - invalid credentials');
            return false;
        }
    }

    logout() {
        localStorage.removeItem(this.sessionKey);
        this.isAuthenticated = false;
        console.log('🚪 User logged out');
    }

    isLoggedIn() {
        return this.isAuthenticated;
    }

    requireAuth() {
        if (!this.isLoggedIn()) {
            console.log('🔒 Authentication required - redirecting to login');
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    getSessionInfo() {
        const sessionData = localStorage.getItem(this.sessionKey);
        if (sessionData) {
            try {
                return JSON.parse(sessionData);
            } catch (error) {
                return null;
            }
        }
        return null;
    }

    getTimeRemaining() {
        const sessionData = this.getSessionInfo();
        if (sessionData) {
            const now = new Date().getTime();
            const remaining = this.sessionTimeout - (now - sessionData.timestamp);
            return Math.max(0, remaining);
        }
        return 0;
    }

    formatTimeRemaining() {
        const remaining = this.getTimeRemaining();
        if (remaining <= 0) return 'Session expired';
        
        const hours = Math.floor(remaining / (60 * 60 * 1000));
        const minutes = Math.floor((remaining % (60 * 60 * 1000)) / (60 * 1000));
        
        if (hours > 0) {
            return `${hours}h ${minutes}m remaining`;
        } else {
            return `${minutes}m remaining`;
        }
    }
}

// Global auth instance
window.auth = new SimpleAuth();

// Auto-check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    // Add auth status to console
    console.log('🔐 Authentication Status:', window.auth.isLoggedIn() ? 'Authenticated' : 'Not authenticated');
    
    // Add session info to console if logged in
    if (window.auth.isLoggedIn()) {
        const sessionInfo = window.auth.getSessionInfo();
        console.log('📊 Session Info:', {
            username: sessionInfo.username,
            loginTime: sessionInfo.loginTime,
            timeRemaining: window.auth.formatTimeRemaining()
        });
    }
});

// Export for use in other modules
export { SimpleAuth };
