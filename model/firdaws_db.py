from config.db import db
from datetime import datetime
import bcrypt
import jwt
import json
from flask import current_app
from config.constant import *




class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Mot de passe en clair pour connexion normale
    password_hash = db.Column(db.String(128), nullable=False)  # Hash pour double authentification
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')

    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_token(self):
        """Génère un token JWT"""
        payload = {
            'user_id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Admin(db.Model):
    """Modèle pour les administrateurs"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='admin')
    photo_url = db.Column(db.String(500), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash le mot de passe avec bcrypt"""
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        # salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_token(self):
        """Génère un token JWT"""
        payload = {
            'admin_id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Document(db.Model):
    """Modèle pour les documents de formation"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    author = db.Column(db.String(100))
    type = db.Column(db.String(50), default='PDF')
    icon = db.Column(db.String(10), default='📄')
    file_size = db.Column(db.String(20))
    file_url = db.Column(db.String(500))
    archived = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'type': self.type,
            'icon': self.icon,
            'file_size': self.file_size,
            'file_url': self.file_url,
            'archived': self.archived,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Event(db.Model):
    """Modèle pour les événements"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='published')
    image_url = db.Column(db.String(500))
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'category': self.category,
            'status': self.status,
            'image_url': self.image_url,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Error(db.Model):
    __tablename__ = 'errors'
    
    id = db.Column(db.Integer, primary_key=True)
    error_type = db.Column(db.String(100))
    message = db.Column(db.Text)
    traceback = db.Column(db.Text)
    endpoint = db.Column(db.String(200))
    method = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'error_type': self.error_type,
            'message': self.message,
            'endpoint': self.endpoint,
            'method': self.method,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class Info(db.Model):
    """Modèle pour les informations/annonces"""
    __tablename__ = 'infos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    is_published = db.Column(db.Boolean, default=True)
    archived = db.Column(db.Boolean, default=False)
    
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'is_published': self.is_published,
            'archived': self.archived,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Mail(db.Model):
    __tablename__ = 'mails'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient': self.recipient,
            'subject': self.subject,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # info, warning, success, error
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()


class Reading(db.Model):
    __tablename__ = 'readings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    source = db.Column(db.String(200))
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    pdf_url = db.Column(db.String(500))
    read_count = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'source': self.source,
            'category': self.category,
            'image_url': self.image_url,
            'pdf_url': self.pdf_url,
            'read_count': self.read_count,
            'is_published': self.is_published,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def increment_read_count(self):
        self.read_count += 1
        self.save()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Training(db.Model):
    __tablename__ = 'trainings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    instructor = db.Column(db.String(100))
    level = db.Column(db.String(50))  # beginner, intermediate, advanced
    duration_hours = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'instructor': self.instructor,
            'level': self.level,
            'duration_hours': self.duration_hours,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'price': self.price,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Video(db.Model):
    """Modèle pour les vidéos YouTube (métadonnées uniquement)"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500), nullable=False)  # URL YouTube complète
    video_id = db.Column(db.String(100))  # ID YouTube extrait de l'URL
    thumbnail_url = db.Column(db.String(500))  # Thumbnail YouTube
    duration = db.Column(db.String(20))
    category = db.Column(db.String(50))  # Correspond aux playlists YouTube
    type = db.Column(db.String(50), default='khutbah')  # ENUM: khutbah, cours, rappel
    view_count = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'video_id': self.video_id,
            'thumbnail_url': self.thumbnail_url or f"https://img.youtube.com/vi/{self.video_id}/0.jpg" if self.video_id else None,
            'duration': self.duration,
            'category': self.category,
            'type': self.type,
            'view_count': self.view_count,
            'is_published': self.is_published,
            'archived': self.archived,
            'created_by': self.created_by,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def increment_view_count(self):
        self.view_count += 1
        self.save()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()



class Khutba(db.Model):
    """Modèle pour les khutba texte"""
    __tablename__ = 'khutba'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20))
    imam = db.Column(db.String(100))
    content = db.Column(db.Text)
    archived = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'imam': self.imam,
            'content': self.content,
            'archived': self.archived
        }

class ResetToken(db.Model):
    """Modèle pour les tokens de réinitialisation"""
    __tablename__ = 'reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    token = db.Column(db.String(500), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FirewallLog(db.Model):
    """Logs du pare-feu et tentatives d'intrusion"""
    __tablename__ = 'firewall_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)
    fingerprint = db.Column(db.String(64), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    attack_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    user_agent = db.Column(db.String(500))
    path = db.Column(db.String(500))
    method = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'fingerprint': self.fingerprint[:20] + '...',
            'severity': self.severity,
            'attack_type': self.attack_type,
            'details': json.loads(self.details) if self.details else {},
            'user_agent': self.user_agent,
            'path': self.path,
            'method': self.method,
            'created_at': self.created_at.isoformat()
        }

class BlockedIP(db.Model):
    """IPs bloquées par le pare-feu"""
    __tablename__ = 'blocked_ips'
    
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False)
    fingerprint = db.Column(db.String(64))
    reason = db.Column(db.String(500))
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'reason': self.reason,
            'expires_at': self.expires_at.isoformat(),
            'expires_in': str(self.expires_at - datetime.utcnow())
        }