"""
Script pour ajouter des données de test dans la base de données Firdaws
"""
from datetime import datetime, timedelta
from model.firdaws_db import db, Event, Document, Info, MosqueLife, Admin
from app import app
import sys

def seed_test_data():
    with app.app_context():
        # Récupérer un admin pour created_by
        admin = Admin.query.first()
        if not admin:
            print("❌ Aucun admin trouvé. Veuillez d'abord créer un admin.")
            return
        
        admin_id = admin.id
        print(f"✅ Utilisation de l'admin ID: {admin_id}")
        
        # ===== ÉVÉNEMENTS =====
        print("\n📅 Ajout des événements...")
        events_data = [
            {
                'title': 'Prières du Ramadan',
                'date': datetime.now() + timedelta(days=7),
                'time': '18:30',
                'imam': 'Imam Ibrahim',
                'description': 'Rejoignez-nous pour les prières spéciales du Ramadan avec Iftar communautaire.',
                'type': 'Khutba',
                'created_by': admin_id
            },
            {
                'title': 'Conférence sur la paix',
                'date': datetime.now() + timedelta(days=14),
                'time': '15:00',
                'imam': 'Imam Youssef',
                'description': 'Une conférence sur l\'importance de la paix dans l\'Islam.',
                'type': 'Conférence',
                'created_by': admin_id
            },
            {
                'title': 'Cours de Coran pour enfants',
                'date': datetime.now() + timedelta(days=3),
                'time': '10:00',
                'imam': 'Imam Ahmed',
                'description': 'Cours d\'apprentissage du Coran pour les enfants de 6 à 12 ans.',
                'type': 'Formation',
                'created_by': admin_id
            },
            {
                'title': 'Repas communautaire',
                'date': datetime.now() + timedelta(days=21),
                'time': '12:00',
                'imam': 'Imam Ibrahim',
                'description': 'Repas partagé après la prière du vendredi.',
                'type': 'Social',
                'created_by': admin_id
            }
        ]
        
        for event_data in events_data:
            existing = Event.query.filter_by(title=event_data['title']).first()
            if not existing:
                # Créer l'événement avec les bons champs
                event = Event(
                    title=event_data['title'],
                    date=event_data['date'],
                    time=event_data['time'],
                    imam=event_data['imam'],
                    description=event_data['description'],
                    type=event_data['type'],
                    created_by_admin=event_data['created_by']
                )
                event.save()
                print(f"  ✅ Événement ajouté: {event_data['title']}")
            else:
                print(f"  ⏭️  Événement existe déjà: {event_data['title']}")
        
        # ===== DOCUMENTS =====
        print("\n📄 Ajout des documents...")
        documents_data = [
            {
                'title': 'Guide des prières',
                'description': 'Guide complet pour effectuer les 5 prières quotidiennes.',
                'file_url': 'https://example.com/guide-prieres.pdf',
                'file_size': '2.5 MB',
                'type': 'PDF',
                'icon': '📄',
                'created_by': admin_id
            },
            {
                'title': 'Calendrier Ramadan 2026',
                'description': 'Calendrier des horaires de prières pour le Ramadan 2026.',
                'file_url': 'https://example.com/calendrier-ramadan.pdf',
                'file_size': '1.2 MB',
                'type': 'PDF',
                'icon': '📄',
                'created_by': admin_id
            },
            {
                'title': 'Formulaire d\'inscription',
                'description': 'Formulaire d\'inscription pour les cours de Coran.',
                'file_url': 'https://example.com/inscription.pdf',
                'file_size': '500 KB',
                'type': 'PDF',
                'icon': '📄',
                'created_by': admin_id
            }
        ]
        
        for doc_data in documents_data:
            existing = Document.query.filter_by(title=doc_data['title']).first()
            if not existing:
                doc = Document(
                    title=doc_data['title'],
                    description=doc_data['description'],
                    file_url=doc_data['file_url'],
                    file_size=doc_data['file_size'],
                    type=doc_data['type'],
                    icon=doc_data['icon'],
                    created_by=doc_data['created_by']
                )
                doc.save()
                print(f"  ✅ Document ajouté: {doc_data['title']}")
            else:
                print(f"  ⏭️  Document existe déjà: {doc_data['title']}")
        
        # ===== ANNONCES (INFOS) =====
        print("\n📢 Ajout des annonces...")
        infos_data = [
            {
                'title': 'Nouveaux horaires de prières',
                'content': 'Les horaires de prières ont été mis à jour pour le mois prochain. Veuillez consulter le tableau d\'affichage.',
                'priority': 'high',
                'type': 'Annonces',
                'created_by': admin_id
            },
            {
                'title': 'Inscriptions ouvertes',
                'content': 'Les inscriptions pour les cours de Coran sont maintenant ouvertes. Contactez le secrétariat.',
                'priority': 'medium',
                'type': 'Informations',
                'created_by': admin_id
            },
            {
                'title': 'Collecte de fonds',
                'content': 'Une collecte de fonds est organisée pour l\'entretien de la mosquée. Tout don est apprécié.',
                'priority': 'medium',
                'type': 'Annonces',
                'created_by': admin_id
            }
        ]
        
        for info_data in infos_data:
            existing = Info.query.filter_by(title=info_data['title']).first()
            if not existing:
                info = Info(
                    title=info_data['title'],
                    content=info_data['content'],
                    priority=info_data['priority'],
                    type=info_data['type'],
                    created_by=info_data['created_by']
                )
                info.save()
                print(f"  ✅ Annonce ajoutée: {info_data['title']}")
            else:
                print(f"  ⏭️  Annonce existe déjà: {info_data['title']}")
        
        # ===== VIE ACTIVE DE LA MOSQUÉE (MOSQUE_LIFE) =====
        print("\n🕌 Ajout de la vie active de la mosquée...")
        mosque_life_data = [
            {
                'title': 'Inauguration de la nouvelle bibliothèque',
                'content': 'Nous sommes ravis d\'annoncer l\'ouverture de notre nouvelle bibliothèque islamique, avec plus de 500 ouvrages disponibles pour la communauté.',
                'category': 'community',
                'image_url': 'https://example.com/bibliotheque.jpg',
                'date': datetime.now().date(),
                'location': 'Mosquée Firdaws',
                'status': 'published',
                'created_by': admin_id
            },
            {
                'title': 'Programme de solidarité Ramadan',
                'content': 'Notre programme de solidarité pour le Ramadan distribue 200 repas par jour aux familles dans le besoin. Rejoignez-nous dans cette initiative.',
                'category': 'social',
                'image_url': 'https://example.com/ramadan-solidarite.jpg',
                'date': datetime.now().date(),
                'location': 'Mosquée Firdaws et environs',
                'status': 'published',
                'created_by': admin_id
            },
            {
                'title': 'Nouveau cours: Introduction à l\'Islam',
                'content': 'Un nouveau cours d\'introduction à l\'Islam commence le mois prochain. Ouvert à tous, sans prérequis. Inscriptions à la mosquée.',
                'category': 'education',
                'image_url': 'https://example.com/cours-islam.jpg',
                'date': datetime.now().date(),
                'location': 'Salle de conférence',
                'status': 'published',
                'created_by': admin_id
            },
            {
                'title': 'Célébration de l\'Aïd',
                'content': 'La communauté se réunira pour célébrer l\'Aïd avec prières, repas et activités pour les enfants. Tous sont bienvenus!',
                'category': 'spiritual',
                'image_url': 'https://example.com/aid-celebration.jpg',
                'date': datetime.now().date(),
                'location': 'Mosquée Firdaws',
                'status': 'published',
                'created_by': admin_id
            }
        ]
        
        for life_data in mosque_life_data:
            existing = MosqueLife.query.filter_by(title=life_data['title']).first()
            if not existing:
                life = MosqueLife(
                    title=life_data['title'],
                    content=life_data['content'],
                    category=life_data['category'],
                    image_url=life_data['image_url'],
                    date=life_data['date'],
                    location=life_data['location'],
                    status=life_data['status'],
                    created_by=life_data['created_by']
                )
                life.save()
                print(f"  ✅ Vie active ajoutée: {life_data['title']}")
            else:
                print(f"  ⏭️  Vie active existe déjà: {life_data['title']}")
        
        print("\n✅ Données de test ajoutées avec succès!")

if __name__ == '__main__':
    seed_test_data()
