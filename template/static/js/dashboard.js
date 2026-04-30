/**
 * dashboard.js - Gestion du panneau d'administration
 */

const Dashboard = {
    /**
     * Initialise le dashboard
     */
    async init() {
        console.log('Initialisation du Dashboard...');
        const user = Auth.getCurrentUser();
        if (!user) {
            Auth.renderLoginForm();
            return;
        }

        // Vérifier si le token est toujours valide
        const isValid = await Auth.checkSession();
        if (!isValid) return;

        this.renderLayout(user);
        this.loadStats();
        this.showSection('events'); // Section par défaut
    },

    /**
     * Affiche la structure de base du dashboard
     */
    renderLayout(user) {
        const container = document.getElementById('dashboardDynamicContent');
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="fw-bold mb-0"><i class="bi bi-speedometer2 me-2"></i>Tableau de bord</h2>
                <div class="d-flex align-items-center">
                    <span class="me-3 text-secondary">Bienvenue, <strong>${user.username}</strong></span>
                    <button class="btn btn-outline-danger btn-sm rounded-pill px-3" onclick="Auth.logout()">
                        <i class="bi bi-box-arrow-right"></i> Déconnexion
                    </button>
                </div>
            </div>

            <div class="row g-4 mb-5">
                <div class="col-md-3">
                    <div class="card-firdaws text-center p-3 h-100" onclick="Dashboard.showSection('events')" style="cursor:pointer">
                        <i class="bi bi-calendar-event fs-2 text-success"></i>
                        <h6 class="mt-2">Événements</h6>
                        <span class="badge bg-light text-dark rounded-pill" id="stat-events">...</span>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-firdaws text-center p-3 h-100" onclick="Dashboard.showSection('videos')" style="cursor:pointer">
                        <i class="bi bi-play-btn fs-2 text-danger"></i>
                        <h6 class="mt-2">Vidéos</h6>
                        <span class="badge bg-light text-dark rounded-pill" id="stat-videos">...</span>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-firdaws text-center p-3 h-100" onclick="Dashboard.showSection('documents')" style="cursor:pointer">
                        <i class="bi bi-file-earmark-pdf fs-2 text-primary"></i>
                        <h6 class="mt-2">Documents</h6>
                        <span class="badge bg-light text-dark rounded-pill" id="stat-docs">...</span>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-firdaws text-center p-3 h-100" onclick="Dashboard.showSection('backlog')" style="cursor:pointer">
                        <i class="bi bi-shield-check fs-2 text-warning"></i>
                        <h6 class="mt-2">Sécurité</h6>
                        <span class="badge bg-light text-dark rounded-pill">Backlog</span>
                    </div>
                </div>
            </div>

            <div id="adminSectionContent">
                <div class="text-center py-5">
                    <div class="spinner-border text-success" role="status"></div>
                </div>
            </div>
        `;
    },

    /**
     * Charge les statistiques globales
     */
    async loadStats() {
        try {
            const stats = await api.tracker.getStats();
            document.getElementById('stat-events').innerText = stats.events || 0;
            document.getElementById('stat-videos').innerText = stats.videos || 0;
            document.getElementById('stat-docs').innerText = stats.documents || 0;
        } catch (error) {
            console.error('Erreur stats:', error);
        }
    },

    /**
     * Change la section affichée
     */
    async showSection(section) {
        const content = document.getElementById('adminSectionContent');
        content.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-success"></div></div>';

        switch(section) {
            case 'events':
                await this.renderEventsManager();
                break;
            case 'videos':
                await this.renderVideosManager();
                break;
            case 'documents':
                await this.renderDocumentsManager();
                break;
            case 'backlog':
                await this.renderBacklogManager();
                break;
        }
    },

    // ========== GESTION DES ÉVÉNEMENTS ==========
    async renderEventsManager() {
        const content = document.getElementById('adminSectionContent');
        try {
            const data = await api.events.getAdmin();
            const events = data.events || [];

            content.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4>Gestion des Événements</h4>
                    <button class="btn btn-firdaws btn-sm rounded-pill" onclick="Dashboard.showEventForm()">
                        <i class="bi bi-plus-lg"></i> Nouvel Événement
                    </button>
                </div>
                <div class="list-group">
                    ${events.map(ev => `
                        <div class="admin-list-item">
                            <div>
                                <strong>${ev.title}</strong>
                                <small class="text-muted ms-2">${ev.date} ${ev.archived ? '<span class="archive-badge">Archivé</span>' : ''}</small>
                            </div>
                            <div class="action-buttons">
                                <button class="btn-action btn-view" onclick="Dashboard.viewItem('events', ${ev.id})"><i class="bi bi-eye"></i></button>
                                <button class="btn-action btn-edit" onclick="Dashboard.editItem('events', ${ev.id})"><i class="bi bi-pencil"></i></button>
                                ${ev.archived 
                                    ? `<button class="btn-action btn-unarchive" onclick="Dashboard.unarchiveItem('events', ${ev.id})"><i class="bi bi-arrow-up-circle"></i></button>`
                                    : `<button class="btn-action btn-archive" onclick="Dashboard.archiveItem('events', ${ev.id})"><i class="bi bi-archive"></i></button>`
                                }
                                <button class="btn-action btn-delete" onclick="Dashboard.deleteItem('events', ${ev.id})"><i class="bi bi-trash"></i></button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            content.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    },

    // ========== GESTION DU BACKLOG ==========
    async renderBacklogManager() {
        const content = document.getElementById('adminSectionContent');
        try {
            const data = await api.tracker.getBacklog();
            const backlog = data.backlog || [];

            content.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4>Journal de Sécurité (Chiffré)</h4>
                    <button class="btn btn-outline-danger btn-sm rounded-pill" onclick="Dashboard.clearBacklog()">
                        <i class="bi bi-eraser"></i> Effacer le journal
                    </button>
                </div>
                <div class="card-firdaws p-0 overflow-hidden">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead class="bg-light">
                                <tr>
                                    <th>Date</th>
                                    <th>Action</th>
                                    <th>IP</th>
                                    <th>Utilisateur</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${backlog.reverse().map(log => `
                                    <tr>
                                        <td><small>${log.timestamp}</small></td>
                                        <td><span class="badge ${log.action.includes('ERROR') ? 'bg-danger' : 'bg-info'}">${log.action}</span></td>
                                        <td><code>${log.ip}</code></td>
                                        <td>${log.user || 'Système'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            content.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    },

    /**
     * Actions CRUD génériques
     */
    async archiveItem(type, id) {
        if (!confirm('Voulez-vous archiver cet élément ?')) return;
        try {
            await api[type].archive(id);
            this.showSection(type);
            Public.init(); // Rafraîchir le public
        } catch (error) {
            alert(error.message);
        }
    },

    async unarchiveItem(type, id) {
        try {
            await api[type].unarchive(id);
            this.showSection(type);
            Public.init();
        } catch (error) {
            alert(error.message);
        }
    },

    async deleteItem(type, id) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer définitivement cet élément ?')) return;
        try {
            await api[type].delete(id);
            this.showSection(type);
            Public.init();
        } catch (error) {
            alert(error.message);
        }
    },

    async clearBacklog() {
        if (!confirm('Voulez-vous vraiment effacer TOUT le journal de sécurité ?')) return;
        try {
            await api.tracker.clearBacklog();
            this.showSection('backlog');
        } catch (error) {
            alert(error.message);
        }
    }
};

// Écouter le clic sur le bouton Admin dans la nav
document.getElementById('dashboardBtn').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('dashboard').style.display = 'block';
    window.location.hash = 'dashboard';
    Dashboard.init();
});
