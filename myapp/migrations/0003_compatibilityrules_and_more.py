# Generated by Django 5.2.3 on 2025-06-29 06:45

import colorfield.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_accessories_footwear_title_occasion_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompatibilityRules',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('vote_count', models.PositiveIntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveIndex(
            model_name='clothingitem',
            name='myapp_cloth_style_9fe019_idx',
        ),
        migrations.RemoveIndex(
            model_name='clothingitem',
            name='myapp_cloth_color_56a8ba_idx',
        ),
        migrations.AddField(
            model_name='accessories',
            name='color',
            field=models.ManyToManyField(blank=True, related_name='accessories', to='myapp.color'),
        ),
        migrations.AddField(
            model_name='accessories',
            name='occasion',
            field=models.ManyToManyField(blank=True, related_name='accessories', to='myapp.occasion'),
        ),
        migrations.AddField(
            model_name='accessories',
            name='style',
            field=models.ManyToManyField(blank=True, related_name='accessories', to='myapp.style'),
        ),
        migrations.AddField(
            model_name='accessories',
            name='title',
            field=models.ManyToManyField(blank=True, related_name='accessories', to='myapp.title'),
        ),
        migrations.AddField(
            model_name='clothingitem',
            name='occasion',
            field=models.ManyToManyField(blank=True, related_name='clothing_items', to='myapp.occasion'),
        ),
        migrations.AddField(
            model_name='color',
            name='hex_code',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None),
        ),
        migrations.AddField(
            model_name='color',
            name='title',
            field=models.ManyToManyField(blank=True, related_name='colors', to='myapp.title'),
        ),
        migrations.AddField(
            model_name='footwear',
            name='color',
            field=models.ManyToManyField(blank=True, related_name='footwears', to='myapp.color'),
        ),
        migrations.AddField(
            model_name='footwear',
            name='occasion',
            field=models.ManyToManyField(blank=True, related_name='footwears', to='myapp.occasion'),
        ),
        migrations.AddField(
            model_name='footwear',
            name='style',
            field=models.ManyToManyField(blank=True, related_name='footwears', to='myapp.style'),
        ),
        migrations.AddField(
            model_name='footwear',
            name='title',
            field=models.ManyToManyField(blank=True, related_name='footwears', to='myapp.title'),
        ),
        migrations.AddField(
            model_name='occasion',
            name='titles',
            field=models.ManyToManyField(blank=True, related_name='occasions', to='myapp.title'),
        ),
        migrations.AddField(
            model_name='style',
            name='titles',
            field=models.ManyToManyField(blank=True, related_name='styles', to='myapp.title'),
        ),
        migrations.RemoveField(
            model_name='clothingitem',
            name='color',
        ),
        migrations.RemoveField(
            model_name='clothingitem',
            name='style',
        ),
        migrations.AlterField(
            model_name='color',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='occasion',
            name='name',
            field=models.CharField(help_text='Type of occasion, e.g., Wedding, Party', max_length=21, unique=True),
        ),
        migrations.AlterField(
            model_name='title',
            name='name',
            field=models.CharField(help_text='Name of your Collection, e.g, Summer Fits, Beach Vacation', max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='compatibilityrules',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.color'),
        ),
        migrations.AddField(
            model_name='compatibilityrules',
            name='occasion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.occasion'),
        ),
        migrations.AddField(
            model_name='compatibilityrules',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.style'),
        ),
        migrations.AddField(
            model_name='clothingitem',
            name='color',
            field=models.ManyToManyField(blank=True, related_name='clothing_items', to='myapp.color'),
        ),
        migrations.AddField(
            model_name='clothingitem',
            name='style',
            field=models.ManyToManyField(blank=True, related_name='clothing_items', to='myapp.style'),
        ),
        migrations.AlterUniqueTogether(
            name='compatibilityrules',
            unique_together={('occasion', 'style', 'color')},
        ),
    ]
