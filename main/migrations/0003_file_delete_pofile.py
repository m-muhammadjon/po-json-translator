# Generated by Django 4.1.4 on 2023-04-20 11:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_pofile_attempts_alter_pofile_from_lang_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['po', 'json'])])),
                ('attempts', models.IntegerField(default=0)),
                ('status', models.CharField(default='Pending', max_length=255)),
                ('result_file', models.URLField(blank=True, null=True)),
                ('from_lang', models.CharField(choices=[('en', 'English'), ('ru', 'Russian'), ('uz', 'Uzbek'), ('cry', 'Cyrillic'), ('kaa', 'Karakalpak')], max_length=10)),
                ('to_lang', models.CharField(choices=[('en', 'English'), ('ru', 'Russian'), ('uz', 'Uzbek'), ('cry', 'Cyrillic'), ('kaa', 'Karakalpak')], max_length=10)),
                ('execution_time', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='PoFile',
        ),
    ]