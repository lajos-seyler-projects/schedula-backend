from django.core.management.base import BaseCommand

from ...models import FilterDefinition
from ..data import FILTER_DEFINITIONS


class Command(BaseCommand):
    help = "Loads default filter definitions into the database"

    def handle(self, *args, **kwargs):
        for table_id, filter_definitions in FILTER_DEFINITIONS.items():
            current_names = set()

            for definition in filter_definitions:
                FilterDefinition.objects.update_or_create(
                    table_id=table_id,
                    name=definition["name"],
                    defaults={
                        "label": definition["label"],
                        "query_parameter": definition["query_parameter"],
                        "required": definition["required"],
                        "is_visible_by_default": definition["is_visible_by_default"],
                    },
                )
                current_names.add(definition["name"])

            FilterDefinition.objects.filter(table_id=table_id).exclude(
                name__in=current_names
            ).delete()
            self.stdout.write(
                self.style.SUCCESS(f"Loaded filter definitions for table: {table_id}")
            )
