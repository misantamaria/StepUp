# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='grupo',
            field=models.CharField(max_length=50, blank=True, null=True, help_text='Grupo del alumno'),
        ),
    ]