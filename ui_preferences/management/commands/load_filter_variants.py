from django.core.management.base import BaseCommand

from ...models import FilterVariant
from ..data.default_filter_variants import DEFAULT_FILTER_VARIANTS


class Command(BaseCommand):
    help = "Loads default filter variants into the database"

    def handle(self, *args, **kwargs):
        for table_id, variants in DEFAULT_FILTER_VARIANTS.items():
            current_names = set()

            for variant in variants:
                name = variant["name"]
                FilterVariant.objects.update_or_create(
                    table_id=table_id,
                    name=name,
                    defaults={"filters": variant.get("filters"), "exclude_filters": variant.get("exclude_filters")},
                )
                current_names.add(name)
            FilterVariant.objects.filter(table_id=table_id).filter(created_by=None).exclude(
                name__in=current_names
            ).delete()
            self.stdout.write(self.style.SUCCESS(f"Loaded default filter variants for table: {table_id}"))
