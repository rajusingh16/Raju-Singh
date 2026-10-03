from django.core.management.base import BaseCommand
from tracker.models import Building, Floor, Room

class Command(BaseCommand):
    help = 'Seed Second Floor rooms for GWCET'

    def handle(self, *args, **options):
        # Get or create building
        building, _ = Building.objects.get_or_create(
            name='Govindrao Wanjari College of Engineering & Technology',
            defaults={
                'description': 'Main academic building',
                'latitude': 21.02138,
                'longitude': 79.12999
            }
        )

        # Get or create Second Floor (Z = 7.32m)
        second_floor, _ = Floor.objects.get_or_create(
            building=building,
            name='Second Floor',
            defaults={
                'floor_number': 2,
                'floor_height_meters': 7.32,
            }
        )

        # Second Floor Rooms (Prototype layout)
        # X = East-West, Y = North-South
        # Origin (0,0) at center of building
        
        rooms_data = [
            # WEST WING (Left side, X negative)
            {'code': 'SF_CLASS_01', 'name': 'Classroom 01', 'type': 'CLASSROOM', 'dept': 'CSE', 'capacity': 60, 'x': -14, 'y': -16, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_02', 'name': 'Classroom 02', 'type': 'CLASSROOM', 'dept': 'CSE', 'capacity': 60, 'x': -14, 'y': -8, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_03', 'name': 'Classroom 03', 'type': 'CLASSROOM', 'dept': 'IT', 'capacity': 60, 'x': -14, 'y': 0, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_04', 'name': 'Classroom 04', 'type': 'CLASSROOM', 'dept': 'IT', 'capacity': 60, 'x': -14, 'y': 8, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_05', 'name': 'Classroom 05', 'type': 'CLASSROOM', 'dept': 'ENTC', 'capacity': 60, 'x': -14, 'y': 16, 'w': 5, 'l': 8.5},
            {'code': 'SF_LAB_01', 'name': 'Computer Lab 01', 'type': 'LABORATORY', 'dept': 'CSE', 'capacity': 40, 'x': -14, 'y': -24, 'w': 8, 'l': 7},
            {'code': 'SF_LAB_02', 'name': 'Software Lab', 'type': 'LABORATORY', 'dept': 'IT', 'capacity': 40, 'x': -14, 'y': 24, 'w': 8, 'l': 7},
            {'code': 'SF_STAFF_01', 'name': 'Staff Room 01', 'type': 'STAFF_ROOM', 'dept': 'CSE', 'capacity': 10, 'x': -6, 'y': -20, 'w': 5, 'l': 6},
            {'code': 'SF_WASHROOM_01', 'name': 'Washroom 01', 'type': 'WASHROOM', 'dept': '', 'capacity': 5, 'x': -6, 'y': -24, 'w': 4, 'l': 5},

            # NORTH WING (Back, Y positive)
            {'code': 'SF_CLASS_06', 'name': 'Classroom 06', 'type': 'CLASSROOM', 'dept': 'MECH', 'capacity': 60, 'x': 0, 'y': 24, 'w': 5, 'l': 8.5},
            {'code': 'SF_LAB_03', 'name': 'Electronics Lab', 'type': 'LABORATORY', 'dept': 'ENTC', 'capacity': 40, 'x': 8, 'y': 24, 'w': 8, 'l': 7},
            {'code': 'SF_STAFF_02', 'name': 'Staff Room 02', 'type': 'STAFF_ROOM', 'dept': 'ENTC', 'capacity': 10, 'x': -8, 'y': 24, 'w': 5, 'l': 6},

            # EAST WING (Right side, X positive)
            {'code': 'SF_CLASS_07', 'name': 'Classroom 07', 'type': 'CLASSROOM', 'dept': 'MECH', 'capacity': 60, 'x': 14, 'y': -16, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_08', 'name': 'Classroom 08', 'type': 'CLASSROOM', 'dept': 'CIVIL', 'capacity': 60, 'x': 14, 'y': -8, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_09', 'name': 'Classroom 09', 'type': 'CLASSROOM', 'dept': 'CIVIL', 'capacity': 60, 'x': 14, 'y': 0, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_10', 'name': 'Classroom 10', 'type': 'CLASSROOM', 'dept': 'EEE', 'capacity': 60, 'x': 14, 'y': 8, 'w': 5, 'l': 8.5},
            {'code': 'SF_CLASS_11', 'name': 'Classroom 11', 'type': 'CLASSROOM', 'dept': 'EEE', 'capacity': 60, 'x': 14, 'y': 16, 'w': 5, 'l': 8.5},
            {'code': 'SF_LAB_04', 'name': 'Electrical Lab', 'type': 'LABORATORY', 'dept': 'EEE', 'capacity': 40, 'x': 14, 'y': -24, 'w': 8, 'l': 7},
            {'code': 'SF_LAB_05', 'name': 'Civil Lab', 'type': 'LABORATORY', 'dept': 'CIVIL', 'capacity': 40, 'x': 14, 'y': 24, 'w': 8, 'l': 7},
            {'code': 'SF_STAFF_03', 'name': 'Staff Room 03', 'type': 'STAFF_ROOM', 'dept': 'MECH', 'capacity': 10, 'x': 6, 'y': -20, 'w': 5, 'l': 6},
            {'code': 'SF_WASHROOM_02', 'name': 'Washroom 02', 'type': 'WASHROOM', 'dept': '', 'capacity': 5, 'x': 6, 'y': -24, 'w': 4, 'l': 5},

            # STAIRCASES (Same position as Ground Floor)
            {'code': 'SF_STAIRS_1', 'name': 'Staircase 1', 'type': 'STAIRCASE', 'dept': '', 'capacity': 20, 'x': -14, 'y': -28, 'w': 4, 'l': 6},
            {'code': 'SF_STAIRS_2', 'name': 'Staircase 2', 'type': 'STAIRCASE', 'dept': '', 'capacity': 20, 'x': 14, 'y': -28, 'w': 4, 'l': 6},

            # CENTRAL COURTYARD (Open to sky - aligned with Ground Floor)
            {'code': 'SF_COURTYARD', 'name': 'Central Courtyard', 'type': 'OTHER', 'dept': '', 'capacity': 0, 'x': 0, 'y': 0, 'w': 10, 'l': 10},
        ]

        for room_data in rooms_data:
            Room.objects.get_or_create(
                room_code=room_data['code'],
                defaults={
                    'name': room_data['name'],
                    'floor': second_floor,
                    'room_type': room_data['type'],
                    'department': room_data['dept'],
                    'capacity': room_data['capacity'],
                    'x': float(room_data['x']),
                    'y': float(room_data['y']),
                    'z': 7.32,  # Second floor height
                    'width': float(room_data['w']),
                    'length': float(room_data['l']),
                    'layout': {
                        'x': room_data['x'],
                        'y': room_data['y'],
                        'width': room_data['w'],
                        'height': room_data['l'],
                    },
                    'description': f"Prototype {room_data['name']} - Department: {room_data['dept']}",
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ Second Floor rooms seeded successfully!'))