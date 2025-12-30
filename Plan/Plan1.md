# Plan: Factory Consignment Management Website

Build a Django 5.0+ web application where admin manages consignments with selectable measurement fields from an editable field library. All field values stored as text without validation (accepts numbers, text, or mixed). Public interface displays all consignments alphabetically. Uses PostgreSQL (Supabase), HTMX, Tailwind CSS, and Railway hosting.

## Steps

1. **Initialize Django project** with Python 3.11+, create `consignment` app, configure Supabase PostgreSQL connection, Railway deployment files (Procfile, railway.json), and install dependencies (Django 5.0+, psycopg2, whitenoise)
2. **Create data models**: `Consignment` (name CharField, created_at), `FieldTemplate` (field_name CharField, admin-manageable), and `ConsignmentMeasurement` (ForeignKeys to Consignment and FieldTemplate, value TextField - no validation)
3. **Build admin authentication** with Django superuser login system, create protected admin views for managing field templates (add/edit/delete field names), and admin dashboard for consignment CRUD operations
4. **Implement consignment creation workflow**: admin enters consignment name, HTMX displays checklist of available `FieldTemplate` entries, admin selects which fields to include and enters values (any text/number/mixed, can be NIL/empty), then saves
5. **Add dynamic field addition** allowing admin to add new measurements to any existing consignment either by selecting from existing field template list or creating brand new custom fields on-the-fly for that specific consignment
6. **Build public read-only interface** with list view showing all consignments alphabetically by name, detail view displaying clicked consignment with all its field measurements, styled with Tailwind CSS via CDN and Heroicons, accessible without authentication

## Architecture: Factory Consignment Management System

### System Overview
Full-stack web application using Django MVC pattern with server-side rendering, HTMX for dynamic interactions, and PostgreSQL database. Two access levels: authenticated admin (full CRUD) and public users (read-only).

### Database Architecture

**Three core tables:**

1. **FieldTemplate**
   - Stores reusable field definitions (e.g., "shank_board", "thickness", "weight")
   - Admin can add/edit/delete field templates
   - Acts as a field library for consignment creation

2. **Consignment**
   - Main entity representing each factory consignment
   - Stores consignment name and timestamp
   - Thousands/lakhs of records expected

3. **ConsignmentMeasurement**
   - Junction table linking Consignment to FieldTemplate
   - Stores actual measurement values as text (no validation)
   - One-to-many: each consignment can have multiple measurements
   - Supports both template-based fields and custom one-off fields

### Application Structure

**Django Project Layout:**
- **Main project** - Settings, URL routing, deployment config
- **Consignment app** - Models, views, templates for all consignment functionality
- **Authentication** - Django built-in auth system (single superuser)

### Authentication & Authorization Flow

**Two access levels:**
- **Public (unauthenticated)** - Read-only access to all consignments and measurements
- **Admin (authenticated)** - Full CRUD on consignments, measurements, and field templates
- Login page with Django session-based authentication
- All admin routes protected with `@login_required` decorator

### Admin Functionality Flow

**Field Template Management:**
- List all field templates
- Add new field template (just field name)
- Edit existing field name
- Delete field template (with cascade handling)

**Consignment Creation:**
1. Admin clicks "Add Consignment"
2. Enters consignment name
3. System displays checklist of all available field templates
4. Admin selects which fields apply to this consignment
5. For each selected field, admin enters value (can be empty/NIL)
6. System creates consignment + all selected measurements in one transaction

**Consignment Management:**
- View all consignments (alphabetically sorted)
- Click consignment to see details with all measurements
- Edit consignment name
- Add new measurements to existing consignment (from template or custom)
- Edit measurement values
- Delete measurements
- Delete entire consignment

**Dynamic Field Addition (Post-Creation):**
- Option 1: Select from existing field templates and add value
- Option 2: Create custom field name on-the-fly for this specific consignment
- Both stored in same ConsignmentMeasurement table

### Public Interface Flow

**Read-Only Views:**
1. **Home/List Page** - Display all consignments alphabetically by name
2. **Detail Page** - Click any consignment to see all its measurements
3. **Search/Filter** (optional) - Find consignments by name
4. No login required, no edit capabilities visible

### Frontend Architecture

**Technology Stack:**
- **HTMX** - Dynamic content loading without full page refreshes
  - Add measurements without reload
  - Update field lists dynamically
  - Submit forms with partial page updates
  
- **Tailwind CSS** - Utility-first styling via CDN
  - Responsive design
  - Modern, clean interface
  - Quick styling without custom CSS

- **Heroicons** - Icon library for UI elements
  - Edit, delete, add icons
  - Visual indicators

**Template Structure:**
- Base template with navigation, auth status
- List templates for consignments, field templates
- Detail templates for individual consignment view
- Form templates for creation/editing
- Partial templates for HTMX responses

### Deployment Architecture

**Platform: Railway**
- Free tier hosting
- Automatic deploys from Git
- Environment variable management
- HTTPS by default

**Database: Supabase PostgreSQL**
- Free tier PostgreSQL
- Remote database connection
- Persistent storage for thousands of records
- Connection pooling

**Static Files:**
- WhiteNoise for serving static files
- Tailwind CSS via CDN (no build step)
- Minimal static assets

**Configuration:**
- Procfile for Railway deployment
- railway.json for service configuration
- Environment variables for secrets (DB credentials, secret key)
- Production settings (DEBUG=False, allowed hosts, CSRF settings)

### Data Flow Examples

**Creating a Consignment:**
1. Admin logs in → Django auth validates → Session created
2. Admin navigates to "Add Consignment" → Django renders form with HTMX
3. Admin enters name → HTMX fetches field template list
4. Admin selects fields (checkboxes) → HTMX shows value inputs
5. Admin fills values → Submit form
6. Django creates Consignment record + multiple ConsignmentMeasurement records
7. HTMX updates page showing new consignment

**Public User Viewing:**
1. User visits site (no login) → Django renders public list view
2. User sees all consignments alphabetically → SQL ORDER BY name
3. User clicks consignment → Django queries Consignment + related Measurements
4. Detail page renders with all field-value pairs
5. No edit buttons visible (template conditional on auth status)

### Scalability Considerations

**For Thousands/Lakhs of Records:**
- Database indexing on Consignment.name for alphabetical sorting
- Pagination on list views (50-100 per page)
- Django query optimization (select_related, prefetch_related)
- Database connection pooling
- Caching for field template list (rarely changes)

This architecture provides clean separation between public and admin interfaces, flexible data model for dynamic fields, and modern UX with minimal JavaScript complexity.

## Implementation Todo List

1. **Setup project dependencies and virtual environment** - Create requirements.txt with Django 5.0+, psycopg2-binary, whitenoise, gunicorn, python-decouple. Initialize virtual environment and install packages.

2. **Initialize Django project structure** - Run django-admin startproject factory_project, create consignment app, verify project structure with manage.py.

3. **Configure database and deployment files** - Create Procfile, railway.json, runtime.txt, .env.example, .gitignore. Configure settings.py for Supabase PostgreSQL connection.

4. **Create database models** - Build FieldTemplate, Consignment, and ConsignmentMeasurement models in models.py with proper relationships and fields.

5. **Create and apply migrations** - Run makemigrations and migrate commands to create database schema from models.

6. **Build Django forms** - Create forms.py with ConsignmentForm, FieldTemplateForm, and MeasurementForm for data input.

7. **Implement view functions** - Create all views in views.py: public views (list, detail), admin views (CRUD operations), auth views, HTMX endpoints.

8. **Configure URL routing** - Set up urls.py for both project and app level, mapping all public and admin routes.

9. **Create base template with Tailwind and HTMX** - Build base.html with Tailwind CDN, HTMX script, navigation, and common layout structure.

10. **Build public templates** - Create consignment_list.html and consignment_detail.html for read-only public access.

11. **Build admin templates** - Create all admin templates: dashboard, consignment forms, field template management, measurement addition.

12. **Create authentication templates** - Build login.html and configure Django authentication system.

13. **Build HTMX partial templates** - Create partial templates for dynamic field selection and measurement updates.

14. **Create superuser and test locally** - Create admin superuser, run development server, test all functionality end-to-end.

15. **Setup Supabase PostgreSQL database** - Create Supabase project, get database credentials, configure connection string.

16. **Deploy to Railway** - Push to Git, connect Railway, configure environment variables, deploy application.
