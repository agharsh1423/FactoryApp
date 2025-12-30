from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from .models import Consignment, FieldTemplate, ConsignmentMeasurement
from .forms import (
    ConsignmentForm, 
    FieldTemplateForm, 
    MeasurementForm,
    ConsignmentWithFieldsForm
)


# ============================================================================
# PUBLIC VIEWS (No Authentication Required)
# ============================================================================

def consignment_list(request):
    """
    Public view: Display all articles alphabetically
    Includes search functionality
    """
    search_query = request.GET.get('search', '')
    
    consignments = Consignment.objects.all().order_by('name')
    
    if search_query:
        consignments = consignments.filter(
            Q(name__icontains=search_query)
        )
    
    context = {
        'consignments': consignments,
        'search_query': search_query,
    }
    
    return render(request, 'public/consignment_list.html', context)


def consignment_detail(request, pk):
    """
    Public view: Display single consignment with all measurements
    """
    consignment = get_object_or_404(Consignment, pk=pk)
    measurements = consignment.measurements.select_related('field_template').all()
    
    context = {
        'consignment': consignment,
        'measurements': measurements,
    }
    return render(request, 'public/consignment_detail.html', context)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def user_login(request):
    """
    Login view for admin access
    """
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


@login_required
def user_logout(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('consignment_list')


# ============================================================================
# ADMIN VIEWS (Authentication Required)
# ============================================================================

@login_required
def admin_dashboard(request):
    """
    Admin dashboard - overview of system
    """
    consignment_count = Consignment.objects.count()
    field_template_count = FieldTemplate.objects.count()
    measurement_count = ConsignmentMeasurement.objects.count()
    recent_consignments = Consignment.objects.order_by('-created_at')[:5]
    
    context = {
        'consignment_count': consignment_count,
        'field_template_count': field_template_count,
        'measurement_count': measurement_count,
        'recent_consignments': recent_consignments,
    }
    return render(request, 'admin/dashboard.html', context)


# ============================================================================
# FIELD TEMPLATE VIEWS (Admin Only)
# ============================================================================

@login_required
def field_template_list(request):
    """
    List all field templates with add/edit/delete options
    """
    templates = FieldTemplate.objects.all().order_by('field_name')
    form = FieldTemplateForm()
    
    context = {
        'templates': templates,
        'form': form,
    }
    return render(request, 'admin/field_template_list.html', context)


@login_required
def field_template_create(request):
    """
    Create new field template
    """
    if request.method == 'POST':
        form = FieldTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Field template "{template.field_name}" created successfully!')
            return redirect('field_template_list')
        else:
            messages.error(request, 'Error creating field template.')
    
    return redirect('field_template_list')


@login_required
def field_template_edit(request, pk):
    """
    Edit existing field template
    """
    template = get_object_or_404(FieldTemplate, pk=pk)
    
    if request.method == 'POST':
        form = FieldTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Field template updated to "{template.field_name}"!')
            return redirect('field_template_list')
        else:
            messages.error(request, 'Error updating field template.')
    else:
        form = FieldTemplateForm(instance=template)
    
    context = {
        'form': form,
        'template': template,
    }
    return render(request, 'admin/field_template_form.html', context)


@login_required
def field_template_delete(request, pk):
    """
    Delete field template
    """
    template = get_object_or_404(FieldTemplate, pk=pk)
    
    if request.method == 'POST':
        field_name = template.field_name
        template.delete()
        messages.success(request, f'Field template "{field_name}" deleted successfully!')
        return redirect('field_template_list')
    
    context = {
        'template': template,
    }
    return render(request, 'admin/field_template_confirm_delete.html', context)


# ============================================================================
# CONSIGNMENT VIEWS (Admin Only)
# ============================================================================

@login_required
def consignment_manage(request):
    """
    Admin view: Manage all consignments
    """
    search_query = request.GET.get('search', '')
    
    consignments = Consignment.objects.all().order_by('name')
    
    if search_query:
        consignments = consignments.filter(Q(name__icontains=search_query))
    
    context = {
        'consignments': consignments,
        'search_query': search_query,
    }
    return render(request, 'admin/consignment_manage.html', context)


@login_required
def consignment_create(request):
    """
    Create new consignment with field selection
    """
    if request.method == 'POST':
        form = ConsignmentWithFieldsForm(request.POST)
        
        if form.is_valid():
            # Create consignment
            consignment_name = form.cleaned_data['name']
            consignment = Consignment.objects.create(name=consignment_name)
            
            # Get all field templates
            field_templates = FieldTemplate.objects.all()
            
            # Create measurements for selected fields
            for template in field_templates:
                field_key = f'field_{template.id}'
                value_key = f'value_{template.id}'
                
                # Check if field was selected
                if form.cleaned_data.get(field_key):
                    value = form.cleaned_data.get(value_key, '')
                    
                    ConsignmentMeasurement.objects.create(
                        consignment=consignment,
                        field_template=template,
                        value=value
                    )
            
            messages.success(request, f'Consignment "{consignment.name}" created successfully!')
            return redirect('consignment_manage')
    else:
        form = ConsignmentWithFieldsForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/consignment_form.html', context)


@login_required
def consignment_edit(request, pk):
    """
    Edit consignment name
    """
    consignment = get_object_or_404(Consignment, pk=pk)
    
    if request.method == 'POST':
        form = ConsignmentForm(request.POST, instance=consignment)
        if form.is_valid():
            consignment = form.save()
            messages.success(request, f'Consignment updated to "{consignment.name}"!')
            return redirect('consignment_manage')
    else:
        form = ConsignmentForm(instance=consignment)
    
    measurements = consignment.measurements.select_related('field_template').all()
    
    context = {
        'form': form,
        'consignment': consignment,
        'measurements': measurements,
    }
    return render(request, 'admin/consignment_edit.html', context)


@login_required
def consignment_delete(request, pk):
    """
    Delete consignment
    """
    consignment = get_object_or_404(Consignment, pk=pk)
    
    if request.method == 'POST':
        consignment_name = consignment.name
        consignment.delete()
        messages.success(request, f'Article "{consignment_name}" deleted successfully!')
        return redirect('consignment_manage')
    
    measurements = consignment.measurements.all()
    
    context = {
        'consignment': consignment,
        'measurements': measurements,
    }
    return render(request, 'admin/consignment_confirm_delete.html', context)


# ============================================================================
# MEASUREMENT VIEWS (Admin Only)
# ============================================================================

@login_required
def measurement_add(request, consignment_pk):
    """
    Add new measurement to existing consignment
    """
    consignment = get_object_or_404(Consignment, pk=consignment_pk)
    
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.consignment = consignment
            measurement.save()
            messages.success(request, 'Measurement added successfully!')
            return redirect('consignment_edit', pk=consignment.pk)
    else:
        form = MeasurementForm()
    
    context = {
        'form': form,
        'consignment': consignment,
    }
    return render(request, 'admin/add_measurement.html', context)


@login_required
def measurement_edit(request, pk):
    """
    Edit existing measurement
    """
    measurement = get_object_or_404(ConsignmentMeasurement, pk=pk)
    
    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Measurement updated successfully!')
            return redirect('consignment_edit', pk=measurement.consignment.pk)
    else:
        form = MeasurementForm(instance=measurement)
    
    context = {
        'form': form,
        'measurement': measurement,
    }
    return render(request, 'admin/measurement_edit.html', context)


@login_required
def measurement_delete(request, pk):
    """
    Delete measurement
    """
    measurement = get_object_or_404(ConsignmentMeasurement, pk=pk)
    consignment_pk = measurement.consignment.pk
    
    if request.method == 'POST':
        measurement.delete()
        messages.success(request, 'Measurement deleted successfully!')
        return redirect('consignment_edit', pk=consignment_pk)
    
    context = {
        'measurement': measurement,
    }
    return render(request, 'admin/measurement_confirm_delete.html', context)


# ============================================================================
# HTMX ENDPOINTS (For Dynamic Updates)
# ============================================================================

@login_required
@require_http_methods(["POST"])
def field_toggle_htmx(request):
    """
    HTMX endpoint: Returns HTML for field value inputs based on selected checkboxes
    """
    # This will be used for dynamic field selection during consignment creation
    # Returns partial HTML for selected field value inputs
    selected_fields = []
    
    for key, value in request.POST.items():
        if key.startswith('field_') and value == 'on':
            template_id = key.replace('field_', '')
            try:
                template = FieldTemplate.objects.get(pk=template_id)
                selected_fields.append(template)
            except FieldTemplate.DoesNotExist:
                pass
    
    context = {
        'selected_fields': selected_fields,
    }
    return render(request, 'partials/field_value_inputs.html', context)

