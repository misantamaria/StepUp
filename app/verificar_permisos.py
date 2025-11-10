from django.contrib.auth.models import User

# Verificar profesor_ayudante
ayudante = User.objects.get(username='profesor_ayudante')
print(f"\n{'='*60}")
print(f"Usuario: {ayudante.username}")
print(f"Email: {ayudante.email}")
print(f"is_staff: {ayudante.is_staff}")
print(f"is_superuser: {ayudante.is_superuser}")
print(f"Grupos: {list(ayudante.groups.values_list('name', flat=True))}")
print(f"\nPermisos:")
print(f"  ✓ Puede crear preguntas: {ayudante.has_perm('boards.add_pregunta')}")
print(f"  ✓ Puede editar preguntas: {ayudante.has_perm('boards.change_pregunta')}")
print(f"  ✗ Puede eliminar preguntas: {ayudante.has_perm('boards.delete_pregunta')}")
print(f"  ✓ Puede crear tests: {ayudante.has_perm('boards.add_test')}")
print(f"  ✗ Puede eliminar tests: {ayudante.has_perm('boards.delete_test')}")

# Verificar profesor
profesor = User.objects.get(username='profesor')
print(f"\n{'='*60}")
print(f"Usuario: {profesor.username}")
print(f"Grupos: {list(profesor.groups.values_list('name', flat=True))}")
print(f"\nPermisos:")
print(f"  ✓ Puede crear preguntas: {profesor.has_perm('boards.add_pregunta')}")
print(f"  ✓ Puede editar preguntas: {profesor.has_perm('boards.change_pregunta')}")
print(f"  ✓ Puede eliminar preguntas: {profesor.has_perm('boards.delete_pregunta')}")
print(f"  ✓ Puede eliminar tests: {profesor.has_perm('boards.delete_test')}")

# Verificar alumno
alumno = User.objects.get(username='alumno')
print(f"\n{'='*60}")
print(f"Usuario: {alumno.username}")
print(f"is_staff: {alumno.is_staff}")
print(f"Grupos: {list(alumno.groups.values_list('name', flat=True))}")
print(f"\nPermisos:")
print(f"  ✗ Puede acceder admin: {alumno.is_staff}")
print(f"  ✗ Puede crear preguntas: {alumno.has_perm('boards.add_pregunta')}")

print(f"\n{'='*60}\n")
