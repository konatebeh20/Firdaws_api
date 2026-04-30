/**
 * APIService - Service central pour toutes les interactions avec l'API
 */
class APIService {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * Méthode générique pour les requêtes API
     */
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('nour_token');
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                // Si le token est expiré ou invalide
                if (response.status === 401) {
                    localStorage.removeItem('nour_token');
                    localStorage.removeItem('nour_user');
                    // Optionnel: rediriger vers le login ou rafraîchir la page
                }
                throw new Error(data.message || 'Une erreur est survenue');
            }

            return data;
        } catch (error) {
            console.error(`Erreur API [${endpoint}]:`, error);
            throw error;
        }
    }

    // ========== AUTHENTIFICATION ==========
    auth = {
        login: (credentials) => this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        }),
        register: (userData) => this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        }),
        verify: () => this.request('/auth/verify'),
        profile: () => this.request('/auth/profile')
    };

    // ========== ÉVÉNEMENTS ==========
    events = {
        getAll: () => this.request('/events'),
        getAdmin: () => this.request('/events/admin'),
        getOne: (id) => this.request(`/events/${id}`),
        create: (data) => this.request('/events', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        update: (id, data) => this.request(`/events/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
        archive: (id) => this.request(`/events/archive/${id}`, {
            method: 'PUT'
        }),
        unarchive: (id) => this.request(`/events/unarchive/${id}`, {
            method: 'PUT'
        }),
        delete: (id) => this.request(`/events/${id}`, {
            method: 'DELETE'
        })
    };

    // ========== VIDÉOS ==========
    videos = {
        getAll: () => this.request('/videos'),
        getAdmin: () => this.request('/videos/admin'),
        getOne: (id) => this.request(`/videos/${id}`),
        create: (data) => this.request('/videos', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        update: (id, data) => this.request(`/videos/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
        delete: (id) => this.request(`/videos/${id}`, {
            method: 'DELETE'
        })
    };

    // ========== DOCUMENTS ==========
    documents = {
        getAll: () => this.request('/documents'),
        getAdmin: () => this.request('/documents/admin'),
        getOne: (id) => this.request(`/documents/${id}`),
        create: (data) => this.request('/documents', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        update: (id, data) => this.request(`/documents/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
        delete: (id) => this.request(`/documents/${id}`, {
            method: 'DELETE'
        })
    };

    // ========== INFOS & ANNONCES ==========
    infos = {
        getAll: () => this.request('/infos'),
        getAdmin: () => this.request('/infos/admin'),
        getOne: (id) => this.request(`/infos/${id}`),
        create: (data) => this.request('/infos', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        update: (id, data) => this.request(`/infos/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
        delete: (id) => this.request(`/infos/${id}`, {
            method: 'DELETE'
        })
    };

    // ========== KHUTBA ==========
    khutba = {
        getAll: () => this.request('/khutba'),
        getAdmin: () => this.request('/khutba/admin'),
        getOne: (id) => this.request(`/khutba/${id}`),
        getLatest: (limit = 5) => this.request(`/khutba/latest?limit=${limit}`),
        create: (data) => this.request('/khutba', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        update: (id, data) => this.request(`/khutba/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
        delete: (id) => this.request(`/khutba/${id}`, {
            method: 'DELETE'
        })
    };

    // ========== TRACKER & BACKLOG ==========
    tracker = {
        getStatus: () => this.request('/tracker/status'),
        getStats: () => this.request('/tracker/stats'),
        getBacklog: () => this.request('/tracker/get_backlog'),
        clearBacklog: () => this.request('/tracker/clear_backlog', {
            method: 'POST'
        })
    };

    // ========== FIREWALL ==========
    firewall = {
        getLogs: () => this.request('/firewall/logs'),
        getBlocked: () => this.request('/firewall/blocked'),
        blockIP: (ip) => this.request('/firewall/block', {
            method: 'POST',
            body: JSON.stringify({ ip })
        }),
        unblockIP: (ip) => this.request('/firewall/unblock', {
            method: 'POST',
            body: JSON.stringify({ ip })
        })
    };

    // ========== FICHIERS ==========
    files = {
        upload: (formData) => {
            const token = localStorage.getItem('nour_token');
            return fetch(`${this.baseURL}/file/upload`, {
                method: 'POST',
                headers: {
                    ...(token && { 'Authorization': `Bearer ${token}` })
                },
                body: formData
            }).then(res => res.json());
        },
        delete: (filename) => this.request(`/file/delete/${filename}`, {
            method: 'DELETE'
        })
    };

    // ========== RECHERCHE ==========
    search = {
        global: (query) => this.request(`/search?q=${encodeURIComponent(query)}`)
    };
}

// Instance globale du service
const api = new APIService();
