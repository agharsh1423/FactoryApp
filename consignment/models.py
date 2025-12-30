from django.db import models
from django.utils import timezone


class FieldTemplate(models.Model):
    """
    Stores reusable field definitions (e.g., 'shank_board', 'thickness', 'weight')
    Admin can create/edit/delete these templates
    Acts as a field library for consignment creation
    """
    field_name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['field_name']
        verbose_name = 'Field Template'
        verbose_name_plural = 'Field Templates'
    
    def __str__(self):
        return self.field_name


class Consignment(models.Model):
    """
    Main entity representing each factory consignment
    Each consignment has a unique name and can have multiple measurements
    """
    name = models.CharField(max_length=200, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']  # Alphabetical order
        verbose_name = 'Consignment'
        verbose_name_plural = 'Consignments'
        indexes = [
            models.Index(fields=['name']),  # Index for fast alphabetical sorting
        ]
    
    def __str__(self):
        return self.name


class ConsignmentMeasurement(models.Model):
    """
    Links consignments to field templates with actual measurement values
    Supports both template-based fields and custom one-off fields
    Values stored as text (no validation - can be numbers, text, or mixed)
    """
    consignment = models.ForeignKey(
        Consignment,
        on_delete=models.CASCADE,
        related_name='measurements'
    )
    field_template = models.ForeignKey(
        FieldTemplate,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='measurements'
    )
    # For custom one-off fields (when field_template is None)
    custom_field_name = models.CharField(max_length=200, blank=True)
    
    # Value stored as text - accepts any input (numbers, text, units like "4.5cm")
    value = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Consignment Measurement'
        verbose_name_plural = 'Consignment Measurements'
        # Ensure a consignment can't have duplicate fields
        unique_together = [['consignment', 'field_template', 'custom_field_name']]
    
    def get_field_name(self):
        """Returns the field name (either from template or custom)"""
        if self.field_template:
            return self.field_template.field_name
        return self.custom_field_name
    
    def __str__(self):
        return f"{self.consignment.name} - {self.get_field_name()}: {self.value}"

