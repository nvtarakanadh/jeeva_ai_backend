#!/bin/bash
# Run migrations before starting the server
python manage.py migrate
# Start Gunicorn server
gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300

