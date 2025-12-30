from django import forms
from .models import Consignment, FieldTemplate, ConsignmentMeasurement


class FieldTemplateForm(forms.ModelForm):
    """
    Form for creating and editing field templates
    Admin uses this to manage the field library
    """
    class Meta:
        model = FieldTemplate
        fields = ['field_name']
        widgets = {
            'field_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter field name'
            })
        }
        labels = {
            'field_name': 'Field Name'
        }


class ConsignmentForm(forms.ModelForm):
    """
    Form for creating and editing consignment names
    """
    class Meta:
        model = Consignment
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter consignment name (e.g., ABZ, Batch-001)'
            })
        }
        labels = {
            'name': 'Consignment Name'
        }


class MeasurementForm(forms.ModelForm):
    """
    Form for adding/editing individual measurements
    Used for adding measurements to existing consignments
    """
    class Meta:
        model = ConsignmentMeasurement
        fields = ['field_template', 'custom_field_name', 'value']
        widgets = {
            'field_template': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'custom_field_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Or enter custom field name'
            }),
            'value': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter value (can be text, number, or mixed)',
                'rows': 3
            })
        }
        labels = {
            'field_template': 'Select Field from Template',
            'custom_field_name': 'Custom Field Name',
            'value': 'Value'
        }
    
    def clean(self):
        """
        Validate that either field_template OR custom_field_name is provided
        """
        cleaned_data = super().clean()
        field_template = cleaned_data.get('field_template')
        custom_field_name = cleaned_data.get('custom_field_name')
        
        if not field_template and not custom_field_name:
            raise forms.ValidationError(
                'Please select a field template or enter a custom field name.'
            )
        
        if field_template and custom_field_name:
            raise forms.ValidationError(
                'Please use either field template or custom field name, not both.'
            )
        
        return cleaned_data


class ConsignmentWithFieldsForm(forms.Form):
    """
    Form for creating a new consignment with field selection
    Displays checkboxes for all available field templates
    Dynamic form that shows value inputs for selected fields
    """
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter consignment name'
        }),
        label='Consignment Name'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically add checkbox for each field template
        field_templates = FieldTemplate.objects.all().order_by('field_name')
        
        for template in field_templates:
            # Checkbox for field selection
            field_key = f'field_{template.id}'
            self.fields[field_key] = forms.BooleanField(
                required=False,
                label=template.field_name,
                widget=forms.CheckboxInput(attrs={
                    'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded',
                    'hx-post': '/admin-panel/consignments/field-toggle/',
                    'hx-trigger': 'change',
                    'hx-target': '#field-values',
                    'hx-swap': 'innerHTML'
                })
            )
            
            # Text input for field value (shown when checkbox is selected)
            value_key = f'value_{template.id}'
            self.fields[value_key] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': f'Enter value for {template.field_name}'
                }),
                label=''
            )
