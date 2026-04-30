from math import ceil

class PaginationHelper:
    """Helper pour la pagination des résultats"""
    
    @staticmethod
    def paginate(query, page=1, per_page=10):
        """Paginate une requête SQLAlchemy"""
        page = max(1, int(page))
        per_page = min(50, max(1, int(per_page)))
        
        total = query.count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        
        pages = ceil(total / per_page) if total > 0 else 0
        
        return {
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
                'has_prev': page > 1,
                'has_next': page < pages,
                'prev_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < pages else None
            }
        }
    
    @staticmethod
    def paginate_dict(items, total, page=1, per_page=10):
        """Paginate une liste de dictionnaires"""
        page = max(1, int(page))
        per_page = min(50, max(1, int(per_page)))
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = items[start:end]
        
        pages = ceil(total / per_page) if total > 0 else 0
        
        return {
            'items': paginated_items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
                'has_prev': page > 1,
                'has_next': page < pages
            }
        }