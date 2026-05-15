import pandas as pd
from django.core.management.base import BaseCommand
from lexi.apps.contracts.models import Contract

class Command(BaseCommand):
    help = "Import contracts from CSV"

    def handle(self, *args, **kwargs):

        df = pd.read_csv(
            "data/contracts/contracts_cleaned_dataset_final_version.xls", 
            encoding="utf-8-sig"
        )

        for _, row in df.iterrows():

            Contract.objects.create(
                name=row["Contract_Name"],
                content=row["Contract_Content"]
            )

        self.stdout.write(
            self.style.SUCCESS("Contracts imported successfully")
        )