import pandas as pd
from django.core.management.base import BaseCommand
from lexi.apps.contracts.models import Contract, Field, ContractField
from lexi.apps.contracts.services.placeholder_service import extract_placeholders
from lexi.apps.contracts.services.field_normalization import normalize

class Command(BaseCommand):
    help = "Import contracts + build fields + relations"

    def handle(self, *args, **kwargs):

        df = pd.read_csv(
            "data/contracts/contracts_cleaned_dataset_final_version.xls",
            encoding="utf-8-sig"
        )

        for _, row in df.iterrows():

            content = row["Contract_Content"]

            contract = Contract.objects.create(
                name=row["Contract_Name"],
                content=content
            )

            placeholders = extract_placeholders(content)

            for ph in set(placeholders):

                ph = normalize(ph)

                if not ph:
                    continue

                field, created = Field.objects.get_or_create(
                    label=ph,
                    defaults={
                        "key": None,
                        "field_type": None
                    }
                )

                ContractField.objects.get_or_create(
                    contract=contract,
                    field=field
                )

        self.stdout.write(self.style.SUCCESS(
            "Import done: contracts + fields + relations created successfully"
        ))