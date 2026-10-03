# GWCET Smart Campus Navigator

Working Django prototype for GWCET indoor navigation. It includes an interactive
2D floor plan, a procedural Three.js campus model, room search/highlighting,
A* routing, QR location anchors, route simulation, editable admin data, and
private expiring WebSocket location shares.

## Run on Windows

From `D:\GWCET_livetracker\campus_navigation`:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_gwcet
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Expected seed output:

```text
GWCET prototype ready: 31 rooms, 50 points, 52 edges.
```

Try the acceptance flow:

1. Search for **Physics Lab**.
2. Select **Physics Laboratory** to highlight it.
3. Keep **Main Gate** as the current location.
4. Press **Navigate here** to draw the A* route in 2D and 3D.
5. Press **Simulate walk** to move the live position marker.

Use the QR button beside Current Location to choose a seeded campus anchor.
Browsers with `BarcodeDetector` support can scan a physical QR payload containing
either a seeded code or JSON such as:

```json
{"building":"GWCET","floor":0,"point":"GF_EAST_CENTER"}
```

## Privacy-safe live tracking demo

Open **Share location**, explicitly tick consent, choose an expiry, and create a
six-character private code. A second browser can enter that code to see only the
updates sent during that temporary session. The demo registry is memory-only,
stops on owner disconnect, and stores no position history.

## Admin and editable layout

Create an administrator with `python manage.py createsuperuser`, then open
`/admin/`. Rooms, dimensions, floors, departments, QR anchors, navigation points,
edge closures, and accessibility flags are editable.

The accepted prototype coordinates live in `tracker/demo_data.py`. They use
`+X = East`, `+Y = North`, and `+Z = Up`. First and second floors intentionally
contain shells only; no exact room layouts are invented.

## Blender / GLB export

The browser model works without Blender. To generate matching named Blender and
GLB assets, install Blender and run:

```powershell
blender --background --python tools\build_gwcet_blender.py -- --output static\models\gwcet_ground_floor.glb
```

Every important mesh is named with its database room code, such as
`GF_COMPUTER_LAB`, so a future GLB loader can highlight it directly.

## Tests

```powershell
python manage.py test
```
