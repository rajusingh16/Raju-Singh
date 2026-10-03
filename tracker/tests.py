from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from channels.testing import WebsocketCommunicator

try:
    from campus_nav.asgi import application
except ImportError:
    from gwcet.asgi import application



from .models import Floor, NavigationPoint, QRLocation, Room
from .pathfinding import shortest_path


class CampusDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_gwcet", verbosity=0)

    def test_seed_creates_expandable_three_floor_structure(self):
        self.assertEqual(Floor.objects.count(), 3)
        self.assertEqual(Room.objects.filter(floor__level=0).count(), 31)
        self.assertTrue(Room.objects.filter(floor__level=2).exists())

    def test_entrance_orientation_matches_accepted_layout(self):
        principal = Room.objects.get(room_code="GF_PRINCIPAL")
        reception = Room.objects.get(room_code="GF_RECEPTION")
        self.assertLess(principal.x, 0, "Principal must be left/west of the entrance.")
        self.assertGreater(reception.x, 0, "Reception must be right/east of the entrance.")

    def test_physics_lab_search(self):
        response = self.client.get(reverse("api-room-search"), {"q": "Physics Lab"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["room_code"], "GF_PHYSICS_LAB")

    def test_alias_search_finds_service_counter(self):
        response = self.client.get(reverse("api-room-search"), {"q": "scholarship"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["room_code"], "GF_ADMISSION")

    def test_search_excludes_inactive_rooms(self):
        Room.objects.filter(room_code="GF_PHYSICS_LAB").update(is_active=False)
        response = self.client.get(reverse("api-room-search"), {"q": "Physics Laboratory"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    def test_bootstrap_contains_geometry_graph_and_qr_anchors(self):
        response = self.client.get(reverse("api-bootstrap"))
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["floors"]), 3)
        self.assertGreaterEqual(len(payload["rooms"]), 30)
        self.assertGreaterEqual(len(payload["navigation_points"]), 45)
        self.assertGreaterEqual(len(payload["edges"]), 50)
        self.assertGreaterEqual(len(payload["qr_locations"]), 10)

    def test_a_star_routes_from_main_gate_to_library(self):
        route = shortest_path("MAIN_GATE", "GF_LIBRARY")
        self.assertEqual(route["points"][0].code, "MAIN_GATE")
        self.assertEqual(route["points"][-1].code, "GF_LIBRARY_DOOR")
        self.assertGreater(route["distance"], 0)

    def test_route_api_supports_accessible_mode(self):
        response = self.client.post(
            reverse("api-route"),
            {"start": "GF_MAIN_ENTRANCE", "destination": "GF_COMPUTER_LAB", "accessible": True},
            content_type="application/json",
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["accessible"])
        self.assertEqual(payload["points"][0]["code"], "GF_MAIN_ENTRANCE")
        self.assertEqual(payload["points"][-1]["code"], "GF_COMPUTER_LAB_DOOR")

    def test_route_api_parses_false_string_as_false(self):
        response = self.client.post(
            reverse("api-route"),
            {"start": "MAIN_GATE", "destination": "GF_LIBRARY", "accessible": "false"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["accessible"])

    def test_qr_anchor_sets_known_navigation_point(self):
        qr = QRLocation.objects.get(code="GWCET-GF-ENTRANCE")
        response = self.client.get(reverse("api-qr", args=[qr.code]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["navigation_point"]["code"], "GF_MAIN_ENTRANCE")

    def test_unknown_route_location_is_rejected(self):
        response = self.client.post(
            reverse("api-route"),
            {"start": "UNKNOWN", "destination": "GF_LIBRARY"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class NavigationPointModelTests(TestCase):
    def test_point_string_uses_stable_code(self):
        floor = Floor.objects.create(
            campus_id=self._campus_id(), level=0, name="Ground Floor", elevation=0
        )
        point = NavigationPoint.objects.create(
            floor=floor, code="TEST_POINT", name="Test", x=0, y=0, z=0
        )
        self.assertEqual(str(point), "TEST_POINT")

    @staticmethod
    def _campus_id():
        from .models import Campus

        return Campus.objects.create(name="Test Campus", code="TEST").id


class PrivacyWebSocketTests(SimpleTestCase):
    async def test_share_requires_explicit_consent(self):
        communicator = WebsocketCommunicator(application, "/ws/tracker/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        self.assertEqual((await communicator.receive_json_from())["event"], "connected")
        await communicator.send_json_to(
            {"action": "start_share", "consent": False, "display_name": "Student", "duration": 15}
        )
        response = await communicator.receive_json_from()
        self.assertEqual(response["event"], "error")
        self.assertIn("consent", response["message"].lower())
        await communicator.disconnect()

    async def test_private_code_delivers_only_joined_updates(self):
        owner = WebsocketCommunicator(application, "/ws/tracker/")
        viewer = WebsocketCommunicator(application, "/ws/tracker/")
        await owner.connect()
        await viewer.connect()
        await owner.receive_json_from()
        await viewer.receive_json_from()
        await owner.send_json_to(
            {"action": "start_share", "consent": True, "display_name": "Student A", "duration": 15}
        )
        started = await owner.receive_json_from()
        await viewer.send_json_to({"action": "join_share", "token": started["token"]})
        joined = await viewer.receive_json_from()
        self.assertEqual(joined["event"], "share_joined")
        await owner.send_json_to(
            {"action": "position_update", "point_code": "GF_EAST_CENTER", "room_name": "East Corridor", "floor": 0, "x": 24, "y": 0, "z": 0}
        )
        await owner.receive_json_from()  # group broadcast also reaches the owner
        update = await viewer.receive_json_from()
        self.assertEqual(update["event"], "position_update")
        self.assertEqual(update["point_code"], "GF_EAST_CENTER")
        await owner.disconnect()
        await viewer.disconnect()

    async def test_invalid_share_duration_and_coordinates_are_handled(self):
        communicator = WebsocketCommunicator(application, "/ws/tracker/")
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.send_json_to(
            {"action": "start_share", "consent": True, "display_name": "  ", "duration": "bad"}
        )
        started = await communicator.receive_json_from()
        self.assertEqual(started["event"], "share_started")
        await communicator.send_json_to(
            {"action": "position_update", "point_code": "MAIN_GATE", "floor": 0, "x": "bad", "y": 0, "z": 0}
        )
        response = await communicator.receive_json_from()
        self.assertEqual(response["event"], "error")
        self.assertIn("numeric", response["message"].lower())
        await communicator.disconnect()
