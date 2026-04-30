/**
 * auth.js - Gestion de l'authentification et des sessions
 */

const Auth = {
    /**
     * Tente de connecter un utilisateur
     */
    async login(email, password, honeypotData = {}) {
        try {
            const response = await api.auth.login({
                email,
                password,
                ...honeypotData
            });

            if (response.token) {
                localStorage.setItem('nour_token', response.token);
                localStorage.setItem('nour_user', JSON.stringify(response.admin));
                return response.admin;
            }
            throw new Error('Erreur de connexion');
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    /**
     * Déconnecte l'utilisateur
     */
    logout() {
        localStorage.removeItem('nour_token');
        localStorage.removeItem('nour_user');
        window.location.reload();
    },

    /**
     * Vérifie si l'utilisateur est connecté
     */
    async checkSession() {
        const token = localStorage.getItem('nour_token');
        if (!token) return false;

        try {
            const response = await api.auth.verify();
            return response.valid;
        } catch (error) {
            this.logout();
            return false;
        }
    },

    /**
     * Récupère l'utilisateur actuel
     */
    getCurrentUser() {
        const user = localStorage.getItem('nour_user');
        return user ? JSON.parse(user) : null;
    },

    /**
     * Affiche le formulaire de login dans le dashboard
     */
    renderLoginForm() {
        const container = document.getElementById('dashboardDynamicContent');
        container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="auth-card">
                        <h2 class="text-center mb-4" style="color: var(--vert-profond);">Administration</h2>
                        <form id="loginForm">
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control rounded-pill px-3" id="loginEmail" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Mot de passe</label>
                                <div class="password-wrapper">
                                    <input type="password" class="form-control rounded-pill px-3" id="loginPassword" required>
                                    <i class="bi bi-eye-slash toggle-password" onclick="Auth.togglePassword('loginPassword', this)"></i>
                                </div>
                            </div>
                            
                            <!-- Honeypot fields -->
                            <div class="honeypot">
                                <input type="text" name="honeypot" id="loginHoneypot">
                                <input type="text" name="website" id="loginWebsite">
                            </div>

                            <button type="submit" class="btn btn-firdaws w-100 rounded-pill mt-3">Se connecter</button>
                            <div class="text-center mt-3">
                                <a href="#" class="forgot-password" onclick="Auth.renderRegisterForm()">Créer un compte</a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const honeypot = document.getElementById('loginHoneypot').value;
            
            try {
                await this.login(email, password, { honeypot });
                Dashboard.init();
            } catch (error) {
                alert(error.message);
            }
        });
    },

    /**
     * Affiche le formulaire d'inscription
     */
    renderRegisterForm() {
        const container = document.getElementById('dashboardDynamicContent');
        container.innerHTML = `
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="auth-card">
                        <h2 class="text-center mb-4" style="color: var(--vert-profond);">Inscription Admin</h2>
                        <form id="registerForm">
                            <div class="mb-3">
                                <label class="form-label">Nom d'utilisateur</label>
                                <input type="text" class="form-control rounded-pill px-3" id="regUsername" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control rounded-pill px-3" id="regEmail" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Mot de passe</label>
                                <div class="password-wrapper">
                                    <input type="password" class="form-control rounded-pill px-3" id="regPassword" required>
                                    <i class="bi bi-eye-slash toggle-password" onclick="Auth.togglePassword('regPassword', this)"></i>
                                </div>
                            </div>
                            
                            <!-- Honeypot fields -->
                            <div class="honeypot">
                                <input type="text" name="honeypot" id="regHoneypot">
                            </div>

                            <button type="submit" class="btn btn-firdaws w-100 rounded-pill mt-3">Créer mon compte</button>
                            <div class="text-center mt-3">
                                <a href="#" class="forgot-password" onclick="Auth.renderLoginForm()">Déjà un compte ? Connexion</a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const honeypot = document.getElementById('regHoneypot').value;

            try {
                await api.auth.register({ username, email, password, honeypot });
                alert('Compte créé avec succès ! Connectez-vous.');
                this.renderLoginForm();
            } catch (error) {
                alert(error.message);
            }
        });
    },

    /**
     * Toggle visibility du mot de passe
     */
    togglePassword(inputId, icon) {
        const input = document.getElementById(inputId);
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        } else {
            input.type = 'password';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        }
    }
};
