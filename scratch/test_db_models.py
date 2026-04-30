import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from config.db import db
from model.firdaws_db import Admin, Event, Video, Info, Document, Khutba, Training, Reading

def run_tests():
    print("\n🚀 DÉMARRAGE DES TESTS DE LA BASE DE DONNÉES FIRDAWS\n")
    print("-" * 50)
    
    with app.app_context():
        results = []
        
        # --- 1. Test ADMIN ---
        try:
            test_admin = Admin(
                username="test_admin_unique",
                email="test_unique@firdaws.com",
                phone="0123456789",
                role="Super Admin"
            )
            test_admin.set_password("password123")
            db.session.add(test_admin)
            db.session.commit()
            results.append(("Admin", True, test_admin.id))
            print("✅ Admin : OK")
        except Exception as e:
            db.session.rollback()
            results.append(("Admin", False, str(e)))
            print(f"❌ Admin : FAILED ({str(e)})")

        # --- 2. Test EVENT ---
        try:
            admin = Admin.query.first()
            test_event = Event(
                title="[TEST] Conférence Annuelle",
                type="Conférence",
                description="Une description de test",
                location="Salle Polyvalente",
                start_date=datetime.now(),
                time="14:00",
                imam="Sheikh Test",
                created_by=admin.id if admin else None
            )
            db.session.add(test_event)
            db.session.commit()
            results.append(("Event", True, test_event.id))
            print("✅ Event : OK")
        except Exception as e:
            db.session.rollback()
            results.append(("Event", False, str(e)))
            print(f"❌ Event : FAILED ({str(e)})")

        # --- 3. Test VIDEO ---
        try:
            test_video = Video(
                title="[TEST] Khutba Jumu'a",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                type="Khutba",
                imam="Imam Test",
                date=datetime.now().strftime('%Y-%m-%d')
            )
            db.session.add(test_video)
            db.session.commit()
            results.append(("Video", True, test_video.id))
            print("✅ Video : OK")
        except Exception as e:
            db.session.rollback()
            results.append(("Video", False, str(e)))
            print(f"❌ Video : FAILED ({str(e)})")

        # --- 4. Test INFO ---
        try:
            test_info = Info(
                title="[TEST] Annonce Importante",
                content="Contenu de test pour les informations.",
                category="Général"
            )
            db.session.add(test_info)
            db.session.commit()
            results.append(("Info", True, test_info.id))
            print("✅ Info : OK")
        except Exception as e:
            db.session.rollback()
            results.append(("Info", False, str(e)))
            print(f"❌ Info : FAILED ({str(e)})")

        # --- 5. Test DOCUMENT ---
        try:
            test_doc = Document(
                title="[TEST] Guide Ramadan",
                description="Description de test",
                author="Auteur Test",
                file_url="https://example.com/test.pdf",
                type="PDF"
            )
            db.session.add(test_doc)
            db.session.commit()
            results.append(("Document", True, test_doc.id))
            print("✅ Document : OK")
        except Exception as e:
            db.session.rollback()
            results.append(("Document", False, str(e)))
            print(f"❌ Document : FAILED ({str(e)})")

        # --- 6. Test KHUTBA (Texte) ---
        try:
            test_khutba = Khutba(
                title="[TEST] L'importance de la patience",
                content="Contenu textuel de la khutba de test.",
                imam="Imam Test",
                date=datetime.now().strftime('%Y-%m-%d')
            )
            db.session.add(test_khutba)
            db.session.commit()
            results.append(("Khutba", True, test_khutba.id))
            print("✅ Khutba : OK")
        except Exception as e:
            db.session.rollback()
            results.append(("Khutba", False, str(e)))
            print(f"❌ Khutba : FAILED ({str(e)})")

        # --- NETTOYAGE (Optionnel, on peut laisser si on veut que l'user voit dans sa base) ---
        print("\n🧹 Nettoyage des données de test...")
        try:
            # On supprime ce qu'on a créé
            for model_name, success, item_id in results:
                if success:
                    if model_name == "Admin": Admin.query.filter_by(id=item_id).delete()
                    if model_name == "Event": Event.query.filter_by(id=item_id).delete()
                    if model_name == "Video": Video.query.filter_by(id=item_id).delete()
                    if model_name == "Info": Info.query.filter_by(id=item_id).delete()
                    if model_name == "Document": Document.query.filter_by(id=item_id).delete()
                    if model_name == "Khutba": Khutba.query.filter_by(id=item_id).delete()
            db.session.commit()
            print("✨ Nettoyage terminé.")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage : {str(e)}")

    print("\n" + "=" * 50)
    print("🏁 RÉSUMÉ FINAL DES TESTS")
    print("-" * 50)
    all_passed = True
    for model_name, success, info in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{model_name:<15} : {status}")
        if not success:
            all_passed = False
            print(f"   Erreur: {info}")
    
    if all_passed:
        print("\n🏆 TOUTES LES FONCTIONNALITÉS DE LA BASE DE DONNÉES SONT OPÉRATIONNELLES !")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ. VÉRIFIEZ LES ERREURS CI-DESSUS.")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    run_tests()
