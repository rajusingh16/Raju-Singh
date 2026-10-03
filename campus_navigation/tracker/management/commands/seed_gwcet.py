import math

from django.core.management.base import BaseCommand
from django.db import transaction

from tracker.demo_data import CORE_EDGES, DEPARTMENTS, FLOORS, POINTS, QR_LOCATIONS, ROOMS
from tracker.models import (
    Campus, Department, Floor, NavigationEdge, NavigationPoint, QRLocation, Room,
)


class Command(BaseCommand):
    help = "Create or update the editable GWCET multi-floor prototype layout."

    @transaction.atomic
    def handle(self, *args, **options):
        campus, _ = Campus.objects.update_or_create(
            code="GWCET",
            defaults={
                "name": "Govindrao Wanjari College of Engineering & Technology",
                "description": "Multi-floor smart-campus 3D navigation prototype.",
            },
        )
        floors = {}
        for spec in FLOORS:
            floor, _ = Floor.objects.update_or_create(
                campus=campus,
                level=spec["level"],
                defaults={
                    "name": spec["name"],
                    "elevation": spec["elevation"],
                    "floor_height": 3.66,
                },
            )
            floors[spec["level"]] = floor

        dept_map = {}
        for short_code, name in DEPARTMENTS:
            dept, _ = Department.objects.update_or_create(short_code=short_code, defaults={"name": name})
            dept_map[short_code] = dept

        points = {}
        for item in POINTS:
            code, name, point_type, floor_level, x, y, z = item
            floor_obj = floors[floor_level]
            point, _ = NavigationPoint.objects.update_or_create(
                code=code,
                defaults={
                    "floor": floor_obj,
                    "name": name,
                    "point_type": point_type,
                    "x": x,
                    "y": y,
                    "z": z,
                    "is_accessible": point_type != "STAIR",
                },
            )
            points[code] = point

        room_edge_specs = []
        for spec in ROOMS:
            floor_level = spec.get("floor_level", 0)
            floor_obj = floors[floor_level]
            z_coord = spec.get("z", 0.0)
            point = None
            if spec["door"]:
                point_code = f'{spec["code"]}_DOOR'
                point, _ = NavigationPoint.objects.update_or_create(
                    code=point_code,
                    defaults={
                        "floor": floor_obj,
                        "name": f'{spec["name"]} door',
                        "point_type": NavigationPoint.PointType.ROOM_DOOR,
                        "x": spec["door"][0],
                        "y": spec["door"][1],
                        "z": z_coord,
                        "is_accessible": True,
                    },
                )
                points[point_code] = point
                room_edge_specs.append((spec["connect"], point_code))
            elif spec["code"] in points:
                point = points[spec["code"]]
            elif spec["code"] == "GF_COURTYARD":
                point = points["GF_COURTYARD_CENTER"]
            elif spec["code"] == "SF_COURTYARD":
                point = points.get("SF_COURTYARD_CENTER")

            dept_obj = dept_map.get(spec.get("department"))

            Room.objects.update_or_create(
                room_code=spec["code"],
                defaults={
                    "floor": floor_obj,
                    "navigation_point": point,
                    "department": dept_obj,
                    "name": spec["name"],
                    "room_type": spec["type"],
                    "wing": spec["wing"],
                    "description": spec.get("description", ""),
                    "aliases": spec.get("aliases", ""),
                    "x": spec["x"],
                    "y": spec["y"],
                    "z": z_coord,
                    "width": spec["width"],
                    "length": spec["length"],
                    "layout": {
                        "x": spec["x"],
                        "y": spec["y"],
                        "width": spec["width"],
                        "height": spec["length"],
                    },
                    "model_object_name": spec["code"],
                    "is_active": True,
                },
            )

        def upsert_edge(start_code, end_code):
            start, end = points[start_code], points[end_code]
            distance = round(math.dist((start.x, start.y, start.z), (end.x, end.y, end.z)), 2)
            a, b = sorted((start, end), key=lambda item: item.code)
            NavigationEdge.objects.update_or_create(
                start_point=a,
                end_point=b,
                defaults={
                    "distance": distance,
                    "accessible": not (a.point_type == "STAIR" or b.point_type == "STAIR"),
                    "stairs": a.point_type == "STAIR" or b.point_type == "STAIR",
                    "lift": False,
                    "is_closed": False,
                },
            )

        for start_code, end_code in [*CORE_EDGES, *room_edge_specs]:
            if start_code in points and end_code in points:
                upsert_edge(start_code, end_code)

        for code, label, point_code in QR_LOCATIONS:
            if point_code in points:
                QRLocation.objects.update_or_create(
                    code=code,
                    defaults={"label": label, "navigation_point": points[point_code]},
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"GWCET prototype ready: {Room.objects.count()} rooms, "
                f"{NavigationPoint.objects.count()} points, {NavigationEdge.objects.count()} edges across 3 floors."
            )
        )
