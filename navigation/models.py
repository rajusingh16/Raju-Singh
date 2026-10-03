from django.db import models

class Building(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    name = models.CharField(max_length=100)
    floor_number = models.IntegerField()  # 0 = Ground, 1 = First, 2 = Second
    floor_height_meters = models.FloatField(default=3.66)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Floor {self.floor_number})"

class Room(models.Model):
    ROOM_TYPES = [
        ('CLASSROOM', 'Classroom'),
        ('LABORATORY', 'Laboratory'),
        ('STAFF_ROOM', 'Staff Room'),
        ('WASHROOM', 'Washroom'),
        ('STAIRCASE', 'Staircase'),
        ('CORRIDOR', 'Corridor'),
        ('DEPARTMENT', 'Department'),
        ('OTHER', 'Other'),
    ]

    room_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='OTHER')
    department = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    capacity = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    # Layout for 2D map (x, y, width, height in floor-plan units)
    layout = models.JSONField(
        default=dict,
        blank=True,
        help_text='Stores {"x": 40, "y": 20, "width": 120, "height": 80}'
    )
    
    # 3D position (meters)
    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)
    z = models.FloatField(default=0.0)
    width = models.FloatField(default=5.0)
    length = models.FloatField(default=8.5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_code} - {self.name}"