from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Field(models.Model):
    TYPE_CHOICES = [
        ('text', 'نص'),
        ('number', 'رقم'),
        ('date', 'تاريخ'),
    ]

    key   = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)
    type  = models.CharField(max_length=50, choices=TYPE_CHOICES, default='text')
    field_type  = models.CharField(max_length=50, choices=TYPE_CHOICES, default='text')


    def __str__(self):
        return f"{self.label} ({self.key})"

class Contract(models.Model):
    CATEGORY_CHOICES = [
        
    ]
    contract_name    = models.CharField(max_length=255)
    contract_content = models.TextField()
    category         = models.CharField(max_length=100, blank=True, default="")
    def __str__(self):
        return self.contract_name

class ContractField(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='contract_fields'
    )
    field    = models.ForeignKey(
        Field,
        on_delete=models.PROTECT,
        related_name='contract_fields'
    )
    label    = models.CharField(
        max_length=255,
    )
    order    = models.PositiveIntegerField(default=0)
    required = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.contract.contract_name} — {self.label}"

class ContractHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contract_history")
    contract = models.ForeignKey("Contract", on_delete=models.SET_NULL, null=True)

    contract_name = models.CharField(max_length=255)
    pdf_url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract_name} - {self.user.id}"