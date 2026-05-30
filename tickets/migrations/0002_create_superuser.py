from django.db import migrations
import os

def create_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Retrieve credentials from environment variables, or use sensible defaults
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"\n>>> Created superuser '{username}' successfully.")

def remove_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"\n>>> Removed superuser '{username}'.")
    except User.DoesNotExist:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(create_superuser, remove_superuser),
    ]
