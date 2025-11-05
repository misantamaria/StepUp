#!/usr/bin/env python
"""Script para arreglar perfiles de usuario duplicados o faltantes"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stepup_config.settings')
django.setup()

from users.models import UserProfile
from django.contrib.auth.models import User
from django.db.models import Count

print("=" * 60)
print("VERIFICANDO PERFILES DE USUARIO")
print("=" * 60)

# 1. Verificar usuarios sin perfil
print("\n1. Verificando usuarios sin perfil...")
users_without_profile = []
for user in User.objects.all():
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        users_without_profile.append(user)
        print(f'   ⚠ Usuario sin perfil: {user.username} (ID: {user.id})')

if not users_without_profile:
    print('   ✓ Todos los usuarios tienen perfil')
else:
    print(f'\n   Creando perfiles faltantes...')
    for user in users_without_profile:
        UserProfile.objects.create(user=user)
        print(f'   ✓ Perfil creado para {user.username}')

# 2. Verificar perfiles duplicados
print("\n2. Verificando perfiles duplicados...")
all_profiles = UserProfile.objects.all()
print(f"   Total de perfiles: {all_profiles.count()}")

duplicates = UserProfile.objects.values('user').annotate(count=Count('id')).filter(count__gt=1)
if duplicates:
    print(f'   ⚠ Perfiles duplicados encontrados: {duplicates.count()}')
    for dup in duplicates:
        user_id = dup['user']
        user = User.objects.get(id=user_id)
        profiles = UserProfile.objects.filter(user=user).order_by('id')
        print(f'\n   Usuario: {user.username} (ID: {user_id}) tiene {profiles.count()} perfiles')
        
        # Mantener el primero, eliminar los demás
        first_profile = profiles.first()
        other_profiles = profiles.exclude(id=first_profile.id)
        
        print(f'   → Manteniendo perfil ID: {first_profile.id}')
        for profile in other_profiles:
            print(f'   → Eliminando perfil duplicado ID: {profile.id}')
            profile.delete()
else:
    print('   ✓ No hay perfiles duplicados')

# 3. Resumen final
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
total_users = User.objects.count()
total_profiles = UserProfile.objects.count()
print(f"Total de usuarios: {total_users}")
print(f"Total de perfiles: {total_profiles}")

if total_users == total_profiles:
    print("✓ ¡Todo correcto! Un perfil por usuario.")
else:
    print("⚠ Hay una discrepancia entre usuarios y perfiles")

print("\n¡Listo!")
