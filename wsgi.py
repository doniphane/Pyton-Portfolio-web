"""Point d'entrée WSGI pour Gunicorn, uWSGI ou les PaaS.

    gunicorn wsgi:app
"""

from app import create_app

app = create_app()
