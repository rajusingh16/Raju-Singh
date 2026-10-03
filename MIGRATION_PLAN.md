# Migration Plan for GWCET LiveTracker

## Phase 1: Create New Apps & Models
```bash
# Create new apps
python manage.py startapp core
python manage.py startapp accounts
python manage.py startapp academics
python manage.py startapp campus
python manage.py startapp attendance
python manage.py startapp exams
python manage.py startapp fees
python manage.py startapp notices
python manage.py startapp library
python manage.py startapp indoor_nav  # renamed from tracker
```

## Phase 2: Settings Configuration
Add to `gwcet/settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'core',
    'accounts',
    'academics',
    'campus',
    'attendance',
    'exams',
    'fees',
    'notices',
    'library',
    'indoor_nav',  # renamed tracker
]

AUTH_USER_MODEL = 'accounts.User'
```

## Phase 3: Data Migration Strategy

### 3.1 Campus Hierarchy Migration
**Source**: `tracker.Campus`, `tracker.Floor`, `tracker.Department`, `tracker.Room`
**Target**: `campus.Campus`, `campus.Building`, `campus.Floor`, `campus.Room`
**Navigation**: `tracker.NavigationPoint`, `tracker.NavigationEdge`, `tracker.QRLocation`, `tracker.UserLocation`, `tracker.LocationShare` → `indoor_nav.*`

### 3.2 Navigation App Migration
**Source**: `navigation.Building`, `navigation.Floor`, `navigation.Room`
**Target**: `campus.Building`, `campus.Floor`, `campus.Room` (deduplicate)

### 3.3 Migration Steps
```bash
# 1. Create initial migrations for new apps
python manage.py makemigrations core accounts academics campus attendance exams fees notices library indoor_nav

# 2. Create data migration scripts
python manage.py makemigrations --empty campus migrate_campus_data
python manage.py makemigrations --empty indoor_nav migrate_navigation_data

# 3. Run migrations
python manage.py migrate --plan  # verify
python manage.py migrate
```

## Phase 4: Data Migration Scripts

### campus/migrations/0002_migrate_campus_data.py
```python
def migrate_campus_data(apps, schema_editor):
    # Migrate tracker.Campus -> campus.Campus
    # Migrate navigation.Building -> campus.Building
    # Migrate tracker.Floor/navigation.Floor -> campus.Floor
    # Migrate tracker.Room/navigation.Room -> campus.Room
    # Migrate tracker.Department -> academics.Department
```

### indoor_nav/migrations/0002_migrate_navigation_data.py
```python
def migrate_navigation_data(apps, schema_editor):
    # Keep tracker navigation models in indoor_nav app
    # Update FK references to new campus models
```

## Phase 5: Cleanup
```bash
# After verifying data migration
# 1. Remove old tracker models (keep navigation graph in indoor_nav)
# 2. Remove navigation app models
# 3. Update all FK references in codebase
# 4. Run final migrations
```

## Rollback Plan
- Keep db.sqlite3 backup before each phase
- Each migration is reversible
- Can rollback to specific migration: `python manage.py migrate campus 0001`