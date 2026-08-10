release: cd esports && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd esports && gunicorn esports.wsgi:application --bind 0.0.0.0:$PORT
