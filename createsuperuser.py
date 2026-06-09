import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_project.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get credentials securely from Render environment variables
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if password:
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser for {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully!")
    else:
        print(f"Superuser '{username}' already exists.")
else:
    print("Skipping superuser creation: DJANGO_SUPERUSER_PASSWORD not set.")