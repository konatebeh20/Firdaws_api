from sqlalchemy import or_
from model.firdaws_db import Event, Video, Document, Info, Khutba

class SearchHelper:
    """Helper pour la recherche globale"""
    
    @staticmethod
    def search_all(query, limit_per_category=5):
        """Recherche dans toutes les catégories"""
        search = f"%{query}%"
        results = {}
        
        # Recherche événements
        events = Event.query.filter(
            Event.archived == False,
            or_(
                Event.title.ilike(search),
                Event.description.ilike(search),
                Event.imam.ilike(search)
            )
        ).limit(limit_per_category).all()
        results['events'] = [e.to_dict() for e in events]
        
        # Recherche vidéos
        videos = Video.query.filter(
            Video.archived == False,
            or_(
                Video.title.ilike(search),
                Video.imam.ilike(search)
            )
        ).limit(limit_per_category).all()
        results['videos'] = [v.to_dict() for v in videos]
        
        # Recherche documents
        documents = Document.query.filter(
            Document.archived == False,
            or_(
                Document.title.ilike(search),
                Document.description.ilike(search)
            )
        ).limit(limit_per_category).all()
        results['documents'] = [d.to_dict() for d in documents]
        
        # Recherche informations
        infos = Info.query.filter(
            Info.archived == False,
            or_(
                Info.title.ilike(search),
                Info.content.ilike(search)
            )
        ).limit(limit_per_category).all()
        results['infos'] = [i.to_dict() for i in infos]
        
        # Recherche khutba
        khutba = Khutba.query.filter(
            Khutba.archived == False,
            or_(
                Khutba.title.ilike(search),
                Khutba.imam.ilike(search),
                Khutba.content.ilike(search)
            )
        ).limit(limit_per_category).all()
        results['khutba'] = [k.to_dict() for k in khutba]
        
        # Total des résultats
        results['total'] = sum(len(v) for v in results.values())
        
        return results
    
    @staticmethod
    def get_search_suggestions(query):
        """Suggestions pour l'autocomplétion"""
        if len(query) < 2:
            return []
        
        search = f"%{query}%"
        suggestions = set()
        
        # Titres d'événements
        events = Event.query.filter(
            Event.archived == False,
            Event.title.ilike(search)
        ).limit(3).all()
        for e in events:
            suggestions.add(e.title)
        
        # Titres de vidéos
        videos = Video.query.filter(
            Video.archived == False,
            Video.title.ilike(search)
        ).limit(3).all()
        for v in videos:
            suggestions.add(v.title)
        
        # Noms d'imams
        imams = Event.query.filter(
            Event.archived == False,
            Event.imam.ilike(search)
        ).limit(3).all()
        for i in imams:
            if i.imam:
                suggestions.add(i.imam)
        
        return list(suggestions)[:10]
