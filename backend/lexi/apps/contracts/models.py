from django.db import models

class Contract(models.Model):

    name = models.CharField(max_length=255)

    content = models.TextField()

    def __str__(self):
        return self.name
    
class Field(models.Model):

    key = models.CharField(
        max_length=255,
        unique=True
    )

    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label
    
class ContractField(models.Model):

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="contract_fields"
    )

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE
    )

    required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.contract.name} - {self.field.label}"