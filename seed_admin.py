from app import app, db
from model.firdaws_db import Admin

with app.app_context():
    # Check if admin already exists
    admin_email = 'admin@firdaws-banco.org'
    existing = Admin.query.filter_by(email=admin_email).first()
    if not existing:
        seed_admin = Admin(
            username='admin_default',
            email=admin_email,
            phone='00000000',
            role='Super Admin'
        )
        seed_admin.set_password('firdaws123')
        seed_admin.save()
        print(f"Admin {admin_email} seeded successfully!")
    else:
        existing.set_password('firdaws123')
        existing.save()
        print(f"Admin {admin_email} updated with default password!")
