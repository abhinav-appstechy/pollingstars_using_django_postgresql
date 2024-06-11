#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations (optional, if you want to migrate the database during build)
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
