release: python manage.py makemigrations
release: python manage.py migrate
worker: celery -A jamboSms worker -l info
web: gunicorn jamboSms.wsgi --log-file -
