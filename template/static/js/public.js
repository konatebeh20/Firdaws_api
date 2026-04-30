/**
 * public.js - Gestion de l'affichage public du site
 */

const Public = {
    /**
     * Initialise toutes les sections publiques
     */
    async init() {
        console.log('Initialisation de la section publique...');
        try {
            await Promise.all([
                this.loadEvents(),
                this.loadVideos(),
                this.loadDocuments(),
                this.loadInfos(),
                this.loadKhutbas()
            ]);
            
            // Mettre à jour le badge de dernière mise à jour
            const badge = document.getElementById('lastUpdateBadge');
            if (badge) {
                const now = new Date();
                badge.innerText = `Mis à jour à ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
            }
        } catch (error) {
            console.error('Erreur lors de l\'initialisation publique:', error);
        }
    },

    /**
     * Charge et affiche les événements
     */
    async loadEvents() {
        const container = document.getElementById('eventsContainer');
        try {
            const data = await api.events.getAll();
            const events = data.events || [];
            
            if (events.length === 0) {
                container.innerHTML = '<div class="col-12 text-center text-muted">Aucun événement à venir</div>';
                return;
            }

            container.innerHTML = events.map(ev => `
                <div class="col-md-6 col-lg-4">
                    <div class="card-firdaws h-100">
                        <span class="badge bg-success bg-opacity-25 text-dark rounded-pill px-3 py-2 mb-2">${ev.type || 'Événement'}</span>
                        <small class="text-secondary d-block mb-2">
                            <i class="bi bi-clock"></i> ${this.formatDate(ev.date)} ${ev.time ? '· ' + ev.time : ''}
                        </small>
                        <h4 style="color: var(--vert-profond);">${ev.title}</h4>
                        <p>${ev.description || ''}</p>
                        ${ev.imam ? `<p class="mb-0"><i class="bi bi-person-circle"></i> ${ev.imam}</p>` : ''}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<div class="col-12 text-center text-danger">Erreur de chargement des événements</div>';
        }
    },

    /**
     * Charge et affiche les vidéos
     */
    async loadVideos() {
        const container = document.getElementById('videosContainer');
        try {
            const data = await api.videos.getAll();
            const videos = data.videos || [];

            if (videos.length === 0) {
                container.innerHTML = '<div class="col-12 text-center text-muted">Aucune vidéo disponible</div>';
                return;
            }

            container.innerHTML = videos.map(v => `
                <div class="col-md-6 col-lg-4">
                    <div class="card-video">
                        <div class="video-thumbnail">
                            <div class="play-button"><i class="bi bi-play-fill"></i></div>
                            ${v.duration ? `<span class="position-absolute top-0 end-0 m-3 bg-dark text-white px-3 py-1 rounded-pill small">${v.duration}</span>` : ''}
                        </div>
                        <div class="p-3">
                            <h5 style="color: var(--vert-profond);">${v.title}</h5>
                            <p class="mb-1"><i class="bi bi-person"></i> ${v.imam || 'Inconnu'}</p>
                            <p class="mb-2"><small class="text-secondary">${this.formatDate(v.created_at)} · ${v.type || 'Vidéo'}</small></p>
                            <a href="${v.video_url || '#'}" target="_blank" class="btn btn-outline-firdaws btn-sm w-100 rounded-pill">Regarder</a>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<div class="col-12 text-center text-danger">Erreur de chargement des vidéos</div>';
        }
    },

    /**
     * Charge et affiche les documents
     */
    async loadDocuments() {
        const container = document.getElementById('documentsContainer');
        try {
            const data = await api.documents.getAll();
            const docs = data.documents || [];

            if (docs.length === 0) {
                container.innerHTML = '<div class="col-12 text-center text-muted">Aucun document disponible</div>';
                return;
            }

            container.innerHTML = docs.map(d => `
                <div class="col-md-6 col-lg-4">
                    <div class="document-item d-flex align-items-center">
                        <span style="font-size: 2.5rem; margin-right: 1rem;">${this.getDocIcon(d.file_type)}</span>
                        <div>
                            <h6 style="color: var(--vert-profond);">${d.title}</h6>
                            <p class="small mb-1">${d.description || ''}</p>
                            <a href="${d.file_url}" target="_blank" class="btn btn-sm btn-firdaws rounded-pill">
                                <i class="bi bi-download"></i> Télécharger
                            </a>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<div class="col-12 text-center text-danger">Erreur de chargement des documents</div>';
        }
    },

    /**
     * Charge et affiche les infos/annonces
     */
    async loadInfos() {
        const container = document.getElementById('infosContainer');
        try {
            const data = await api.infos.getAll();
            const infos = data.infos || [];

            if (infos.length === 0) {
                container.innerHTML = '<p class="text-muted">Aucune annonce</p>';
                return;
            }

            container.innerHTML = infos.map(i => `
                <div class="d-flex mb-4 p-3 bg-white rounded-4 shadow-sm">
                    <i class="bi bi-info-square fs-3 me-3" style="color: var(--vert-profond);"></i>
                    <div><strong>${i.title}</strong><br>${i.content}</div>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p class="text-danger">Erreur de chargement des annonces</p>';
        }
    },

    /**
     * Charge et affiche les khutbas
     */
    async loadKhutbas() {
        const container = document.getElementById('khutbaContainer');
        try {
            const data = await api.khutba.getLatest(5);
            const khutbas = data.khutbas || [];

            if (khutbas.length === 0) {
                container.innerHTML = '<p class="text-muted">Aucune khutba disponible</p>';
                return;
            }

            container.innerHTML = khutbas.map(k => `
                <div class="border-bottom pb-3 mb-3">
                    <h5><i class="bi bi-file-text me-2" style="color: var(--or-doux);"></i> ${k.title}</h5>
                    <p class="text-secondary">${this.formatDate(k.date)} · ${k.imam}</p>
                </div>
            `).join('');
        } catch (error) {
            container.innerHTML = '<p class="text-danger">Erreur de chargement des khutbas</p>';
        }
    },

    /**
     * Helpers de formatage
     */
    formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    },

    getDocIcon(type) {
        const icons = {
            'pdf': '📄',
            'doc': '📘',
            'docx': '📘',
            'xls': '📊',
            'xlsx': '📊',
            'zip': '📦'
        };
        return icons[type?.toLowerCase()] || '📄';
    }
};

// Lancement au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    Public.init();
});
