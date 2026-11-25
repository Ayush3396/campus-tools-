"""
marketplace/management/commands/load_categories.py

A custom Django management command.
Run it with: python manage.py load_categories

Management commands let you write Python scripts that work inside
Django's environment (with database access, models, etc.)
They are run from the terminal just like manage.py migrate or runserver.
"""

from django.core.management.base import BaseCommand
from marketplace.models import Category


class Command(BaseCommand):
    # This text shows up when you run: python manage.py help load_categories
    help = 'Loads the initial set of item categories into the database'

    def handle(self, *args, **options):
        """
        handle() is the method that runs when the command is executed.
        self.stdout.write() prints to the terminal.
        self.style.SUCCESS() makes the text green.
        """

        categories = [
            {
                'name': 'Books & Notes',
                'description': 'Textbooks, reference books, handwritten notes, printed notes'
            },
            {
                'name': 'Electronics',
                'description': 'Chargers, earphones, power banks, USB drives, keyboards, mice'
            },
            {
                'name': 'Calculators',
                'description': 'Scientific calculators, graphing calculators, basic calculators'
            },
            {
                'name': 'Lab Equipment',
                'description': 'Lab coats, goggles, dissection kits, measuring instruments'
            },
            {
                'name': 'Sports Equipment',
                'description': 'Cricket bats, footballs, badminton rackets, skipping ropes'
            },
            {
                'name': 'Tools',
                'description': 'Screwdrivers, soldering kits, multimeters, pliers'
            },
            {
                'name': 'Stationery',
                'description': 'Geometry boxes, drawing boards, rulers, markers, pens'
            },
            {
                'name': 'Accessories',
                'description': 'Bags, water bottles, umbrellas, locks'
            },
            {
                'name': 'Other',
                'description': 'Items that do not fit into any other category'
            },
        ]

        created_count = 0
        skipped_count = 0

        for cat_data in categories:
            # get_or_create returns (object, created)
            # created is True if the object was newly created, False if it already existed
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {category.name}")
            else:
                skipped_count += 1
                self.stdout.write(f"  Already exists: {category.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! {created_count} categories created, {skipped_count} already existed.'
            )
        )
