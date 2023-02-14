# Generated by Django 3.2.12 on 2023-02-13 16:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        ('locations', '0001_initial'),
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobsStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_available', models.IntegerField()),
                ('total_unavailable', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=300)),
                ('category', models.CharField(max_length=300)),
                ('sub_category', models.CharField(default='', max_length=300)),
                ('post', models.CharField(max_length=100000)),
                ('required_experience', models.IntegerField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('job_id', models.CharField(max_length=300)),
                ('job_url', models.CharField(max_length=1000)),
                ('reviewed', models.BooleanField(default=False)),
                ('available', models.BooleanField(default=True)),
                ('unavailable_date', models.DateTimeField(blank=True, null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company', to='companies.company')),
                ('location', models.ManyToManyField(related_name='locations', to='locations.Locations')),
                ('required_skills', models.ManyToManyField(related_name='skills', to='skills.Skills')),
            ],
            options={
                'unique_together': {('job_id', 'company')},
            },
        ),
    ]