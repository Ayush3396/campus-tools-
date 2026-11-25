"""
0002_seed_categories.py

Seeds the predefined item categories into the database.
Run:  python manage.py migrate
"""

from django.db import migrations


CATEGORIES = [
    ("Books & Notes", "Textbooks, notebooks, study guides, and reference materials"),
    ("Electronics", "Phones, laptops, chargers, headphones, and other electronic devices"),
    ("Calculators", "Scientific, graphing, and financial calculators"),
    ("Lab Equipment", "Laboratory apparatus, glassware, and science equipment"),
    ("Sports Equipment", "Cricket bats, footballs, badminton rackets, and sports gear"),
    ("Tools", "Screwdrivers, wrenches, hammers, and general tools"),
    ("Stationery", "Pens, pencils, markers, folders, and office supplies"),
    ("Accessories", "Bags, belts, watches, and personal accessories"),
    ("Other", "Items that do not fit into any specific category"),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    for name, description in CATEGORIES:
        Category.objects.get_or_create(name=name, defaults={'description': description})


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    Category.objects.filter(name__in=[c[0] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
