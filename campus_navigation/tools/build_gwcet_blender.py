"""Generate the lightweight GWCET ground-floor model and export GLB.

Run from the campus_navigation directory with Blender installed:
blender --background --python tools/build_gwcet_blender.py -- --output static/models/gwcet_ground_floor.glb

The web prototype builds equivalent geometry directly in Three.js, so Blender is
not required to run the Django app. This script creates named meshes that match
Room.model_object_name for a later GLB-based viewer.
"""

import argparse
import sys
from pathlib import Path

import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from tracker.demo_data import ROOMS


COLORS = {
    "ADMINISTRATION": (0.67, 0.38, 0.10, 1),
    "CLASSROOM": (0.25, 0.55, 0.52, 1),
    "LABORATORY": (0.18, 0.43, 0.68, 1),
    "LIBRARY": (0.46, 0.30, 0.66, 1),
    "STAFF_ROOM": (0.59, 0.34, 0.23, 1),
    "WASHROOM": (0.22, 0.55, 0.68, 1),
    "STAIRCASE": (0.42, 0.47, 0.46, 1),
    "ENTRANCE": (0.20, 0.58, 0.39, 1),
    "SERVICE_COUNTER": (0.69, 0.43, 0.20, 1),
    "OTHER": (0.34, 0.55, 0.27, 1),
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="static/models/gwcet_ground_floor.glb")
    parser.add_argument("--blend", default="static/models/gwcet_ground_floor.blend")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def collection(name, parent=None):
    result = bpy.data.collections.new(name)
    (parent.children if parent else bpy.context.scene.collection.children).link(result)
    return result


def material(name, color, metallic=0.0, roughness=0.75):
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.metallic = metallic
    result.roughness = roughness
    return result


def cube(name, location, dimensions, material_value, target_collection):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material_value)
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    target_collection.objects.link(obj)
    return obj


def cylinder(name, location, radius, depth, material_value, target_collection):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material_value)
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    target_collection.objects.link(obj)
    return obj


def build():
    args = parse_args()
    output_path = (PROJECT_ROOT / args.output).resolve()
    blend_path = (PROJECT_ROOT / args.blend).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for old_collection in list(bpy.data.collections):
        bpy.data.collections.remove(old_collection)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT"

    root = collection("GWCET")
    site = collection("SITE", root)
    ground = collection("GROUND_FLOOR", root)
    administration = collection("ADMIN", ground)
    west = collection("WEST_WING", ground)
    north = collection("NORTH_WING", ground)
    east = collection("EAST_WING", ground)
    courtyard_collection = collection("COURTYARD", ground)
    stairs = collection("STAIRS", ground)
    collection("FIRST_FLOOR", root)
    collection("SECOND_FLOOR", root)

    materials = {key: material(f"MAT_{key}", value) for key, value in COLORS.items()}
    slab_material = material("MAT_FLOOR", (0.72, 0.76, 0.72, 1))
    grass_material = material("MAT_GRASS", (0.24, 0.52, 0.24, 1))
    path_material = material("MAT_PATH", (0.62, 0.61, 0.55, 1))
    trunk_material = material("MAT_TREE_TRUNK", (0.32, 0.19, 0.09, 1))

    cube("SITE_GROUND", (0, 0, -0.35), (180, 175, 0.5), grass_material, site)
    cube("APPROACH_PATH", (0, -50, -0.03), (9, 34, 0.18), path_material, site)
    cube("PARKING", (-45, -52, -0.02), (58, 34, 0.16), material("MAT_PARKING", (0.28, 0.33, 0.33, 1)), site)
    cube("PLAYGROUND", (51, -51, -0.02), (54, 38, 0.16), material("MAT_PLAYGROUND", (0.56, 0.47, 0.24, 1)), site)
    cube("MAIN_GATE_LEFT", (-6, -62, 2.5), (1.7, 1.7, 5.5), material("MAT_GATE", (0.03, 0.16, 0.19, 1)), site)
    cube("MAIN_GATE_RIGHT", (6, -62, 2.5), (1.7, 1.7, 5.5), bpy.data.materials["MAT_GATE"], site)
    cube("MAIN_GATE_BEAM", (0, -62, 5.1), (13.5, 1.4, 1.2), bpy.data.materials["MAT_GATE"], site)

    cube("GROUND_SLAB", (4, 0, -0.1), (96, 78, 0.4), slab_material, ground)
    cube("GF_COURTYARD", (0, 0, 0.12), (31, 31, 0.24), grass_material, courtyard_collection)
    cube("COURTYARD_PATH_NS", (0, 0, 0.28), (3.2, 31, 0.08), path_material, courtyard_collection)
    cube("COURTYARD_PATH_EW", (0, 0, 0.29), (31, 3.2, 0.08), path_material, courtyard_collection)

    for index, (x, y) in enumerate(((-9, -9), (9, -9), (-9, 9), (9, 9)), start=1):
        cylinder(f"COURTYARD_TREE_{index}_TRUNK", (x, y, 1.0), .25, 2, trunk_material, courtyard_collection)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.4, location=(x, y, 2.7))
        crown = bpy.context.object
        crown.name = f"COURTYARD_TREE_{index}_CROWN"
        crown.data.materials.append(grass_material)
        for existing in list(crown.users_collection):
            existing.objects.unlink(crown)
        courtyard_collection.objects.link(crown)

    for room in ROOMS:
        if room["code"] == "GF_COURTYARD":
            continue
        if room["type"] in ("ADMINISTRATION", "SERVICE_COUNTER", "STAFF_ROOM", "ENTRANCE"):
            target = administration
        elif room["type"] == "STAIRCASE":
            target = stairs
        elif room["wing"].startswith("West"):
            target = west
        elif room["wing"].startswith("North"):
            target = north
        else:
            target = east
        height = 1.5 if room["type"] == "ENTRANCE" else 2.8
        cube(
            room["code"],
            (room["x"], room["y"], height / 2 + 0.2),
            (room["width"] - 0.25, room["length"] - 0.25, height),
            materials[room["type"]],
            target,
        )

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
    )
    print(f"Saved Blender source: {blend_path}")
    print(f"Exported GLB: {output_path}")


if __name__ == "__main__":
    build()
