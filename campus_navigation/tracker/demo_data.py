"""Editable prototype layout for GWCET ground, first, and second floor navigation.

Coordinates use +X east, +Y north and +Z up. Dimensions are metres.
Second floor is modeled as a realistic prototype connected via aligned Staircases.
"""

FLOORS = [
    {"level": 0, "name": "Ground Floor", "elevation": 0.0},
    {"level": 1, "name": "First Floor", "elevation": 3.66},
    {"level": 2, "name": "Second Floor", "elevation": 7.32},
]

DEPARTMENTS = [
    ("CSE", "Computer Science & Engineering"),
    ("CSE-DS", "Computer Science & Engineering (Data Science)"),
    ("ETC", "Electronics & Telecommunication"),
    ("IT", "Information Technology"),
    ("CIVIL", "Civil Engineering"),
    ("EE", "Electrical Engineering"),
    ("MECH", "Mechanical Engineering"),
]

# (code, name, point_type, floor_level, x, y, z)
POINTS = [
    # Ground Floor (Z=0)
    ("MAIN_GATE", "Main Gate", "GATE", 0, 0, -62, 0.0),
    ("APPROACH_PATH", "Approach Path", "CORRIDOR", 0, 0, -50, 0.0),
    ("GF_MAIN_ENTRANCE", "Main Entrance", "ENTRANCE", 0, 0, -39, 0.0),
    ("GF_FRONT_CENTER", "Front Corridor", "CORRIDOR", 0, 0, -24, 0.0),
    ("GF_FRONT_WEST", "Front Corridor · West", "CORRIDOR", 0, -18, -24, 0.0),
    ("GF_FRONT_EAST", "Front Corridor · East", "CORRIDOR", 0, 18, -24, 0.0),
    ("GF_WEST_SOUTH", "West Corridor · South", "CORRIDOR", 0, -24, -13, 0.0),
    ("GF_WEST_CENTER", "West Corridor", "CORRIDOR", 0, -24, 0, 0.0),
    ("GF_WEST_NORTH", "West Corridor · North", "CORRIDOR", 0, -24, 13, 0.0),
    ("GF_NORTH_WEST", "North Corridor · West", "CORRIDOR", 0, -18, 24, 0.0),
    ("GF_NORTH_CENTER", "North Corridor", "CORRIDOR", 0, 0, 24, 0.0),
    ("GF_NORTH_EAST", "North Corridor · East", "CORRIDOR", 0, 18, 24, 0.0),
    ("GF_EAST_NORTH", "East Corridor · North", "CORRIDOR", 0, 24, 13, 0.0),
    ("GF_EAST_CENTER", "East Corridor", "CORRIDOR", 0, 24, 0, 0.0),
    ("GF_EAST_SOUTH", "East Corridor · South", "CORRIDOR", 0, 24, -13, 0.0),
    ("GF_EXT_NORTH", "East Academic Extension · North", "CORRIDOR", 0, 38, 12, 0.0),
    ("GF_EXT_CENTER", "East Academic Extension", "CORRIDOR", 0, 38, 0, 0.0),
    ("GF_EXT_SOUTH", "East Academic Extension · South", "CORRIDOR", 0, 38, -12, 0.0),
    ("GF_COURTYARD_SOUTH", "Courtyard · South", "COURTYARD", 0, 0, -17, 0.0),
    ("GF_COURTYARD_CENTER", "Central Courtyard", "COURTYARD", 0, 0, 0, 0.0),
    ("GF_COURTYARD_NORTH", "Courtyard · North", "COURTYARD", 0, 0, 17, 0.0),
    ("GF_STAIRS_1", "Staircase 1", "STAIR", 0, -24, 16, 0.0),
    ("GF_STAIRS_2", "Staircase 2", "STAIR", 0, 24, -5, 0.0),

    # First Floor (Z=3.66) Stair Connectors
    ("FF_STAIRS_1", "First Floor Staircase 1", "STAIR", 1, -24, 16, 3.66),
    ("FF_STAIRS_2", "First Floor Staircase 2", "STAIR", 1, 24, -5, 3.66),

    # Second Floor (Z=7.32)
    ("SF_STAIRS_1", "Second Floor Staircase 1", "STAIR", 2, -24, 16, 7.32),
    ("SF_STAIRS_2", "Second Floor Staircase 2", "STAIR", 2, 24, -5, 7.32),
    ("SF_FRONT_CENTER", "Second Floor Front Corridor", "CORRIDOR", 2, 0, -24, 7.32),
    ("SF_FRONT_WEST", "Second Floor Front Corridor · West", "CORRIDOR", 2, -18, -24, 7.32),
    ("SF_FRONT_EAST", "Second Floor Front Corridor · East", "CORRIDOR", 2, 18, -24, 7.32),
    ("SF_WEST_SOUTH", "Second Floor West Corridor · South", "CORRIDOR", 2, -24, -13, 7.32),
    ("SF_WEST_CENTER", "Second Floor West Corridor", "CORRIDOR", 2, -24, 0, 7.32),
    ("SF_WEST_NORTH", "Second Floor West Corridor · North", "CORRIDOR", 2, -24, 13, 7.32),
    ("SF_NORTH_WEST", "Second Floor North Corridor · West", "CORRIDOR", 2, -18, 24, 7.32),
    ("SF_NORTH_CENTER", "Second Floor North Corridor", "CORRIDOR", 2, 0, 24, 7.32),
    ("SF_NORTH_EAST", "Second Floor North Corridor · East", "CORRIDOR", 2, 18, 24, 7.32),
    ("SF_EAST_NORTH", "Second Floor East Corridor · North", "CORRIDOR", 2, 24, 13, 7.32),
    ("SF_EAST_CENTER", "Second Floor East Corridor", "CORRIDOR", 2, 24, 0, 7.32),
    ("SF_EAST_SOUTH", "Second Floor East Corridor · South", "CORRIDOR", 2, 24, -13, 7.32),
    ("SF_COURTYARD_CENTER", "Second Floor Courtyard Opening", "COURTYARD", 2, 0, 0, 7.32),
]

CORE_EDGES = [
    # Ground Floor Loop
    ("MAIN_GATE", "APPROACH_PATH"),
    ("APPROACH_PATH", "GF_MAIN_ENTRANCE"),
    ("GF_MAIN_ENTRANCE", "GF_FRONT_CENTER"),
    ("GF_FRONT_CENTER", "GF_FRONT_WEST"),
    ("GF_FRONT_CENTER", "GF_FRONT_EAST"),
    ("GF_FRONT_WEST", "GF_WEST_SOUTH"),
    ("GF_WEST_SOUTH", "GF_WEST_CENTER"),
    ("GF_WEST_CENTER", "GF_WEST_NORTH"),
    ("GF_WEST_NORTH", "GF_NORTH_WEST"),
    ("GF_NORTH_WEST", "GF_NORTH_CENTER"),
    ("GF_NORTH_CENTER", "GF_NORTH_EAST"),
    ("GF_NORTH_EAST", "GF_EAST_NORTH"),
    ("GF_EAST_NORTH", "GF_EAST_CENTER"),
    ("GF_EAST_CENTER", "GF_EAST_SOUTH"),
    ("GF_EAST_SOUTH", "GF_FRONT_EAST"),
    ("GF_EAST_NORTH", "GF_EXT_NORTH"),
    ("GF_EXT_NORTH", "GF_EXT_CENTER"),
    ("GF_EXT_CENTER", "GF_EXT_SOUTH"),
    ("GF_EXT_SOUTH", "GF_EAST_SOUTH"),
    ("GF_FRONT_CENTER", "GF_COURTYARD_SOUTH"),
    ("GF_COURTYARD_SOUTH", "GF_COURTYARD_CENTER"),
    ("GF_COURTYARD_CENTER", "GF_COURTYARD_NORTH"),
    ("GF_COURTYARD_NORTH", "GF_NORTH_CENTER"),
    ("GF_WEST_NORTH", "GF_STAIRS_1"),
    ("GF_EAST_CENTER", "GF_STAIRS_2"),

    # Vertical Stair Connections (GF -> FF -> SF)
    ("GF_STAIRS_1", "FF_STAIRS_1"),
    ("FF_STAIRS_1", "SF_STAIRS_1"),
    ("GF_STAIRS_2", "FF_STAIRS_2"),
    ("FF_STAIRS_2", "SF_STAIRS_2"),

    # Second Floor Loop
    ("SF_WEST_NORTH", "SF_STAIRS_1"),
    ("SF_EAST_CENTER", "SF_STAIRS_2"),
    ("SF_FRONT_CENTER", "SF_FRONT_WEST"),
    ("SF_FRONT_CENTER", "SF_FRONT_EAST"),
    ("SF_FRONT_WEST", "SF_WEST_SOUTH"),
    ("SF_WEST_SOUTH", "SF_WEST_CENTER"),
    ("SF_WEST_CENTER", "SF_WEST_NORTH"),
    ("SF_WEST_NORTH", "SF_NORTH_WEST"),
    ("SF_NORTH_WEST", "SF_NORTH_CENTER"),
    ("SF_NORTH_CENTER", "SF_NORTH_EAST"),
    ("SF_NORTH_EAST", "SF_EAST_NORTH"),
    ("SF_EAST_NORTH", "SF_EAST_CENTER"),
    ("SF_EAST_CENTER", "SF_EAST_SOUTH"),
    ("SF_EAST_SOUTH", "SF_FRONT_EAST"),
]


def room(code, name, kind, wing, x, y, width, length, door, connect, floor_level=0, z=0.0, aliases="", description="", capacity=40, dept=None):
    return {
        "code": code,
        "name": name,
        "type": kind,
        "wing": wing,
        "x": x,
        "y": y,
        "z": z,
        "floor_level": floor_level,
        "width": width,
        "length": length,
        "door": door,
        "connect": connect,
        "aliases": aliases,
        "description": description or f"{name}, located in the {wing.lower()} area.",
        "capacity": capacity,
        "department": dept,
    }


ROOMS = [
    # Ground Floor Rooms (Z=0)
    room("GF_MAIN_ENTRANCE", "Main Entrance", "ENTRANCE", "South", 0, -39, 9, 5, None, None, 0, 0.0, "foyer,porch"),
    room("GF_PRINCIPAL", "Principal Cabin", "ADMINISTRATION", "South-West", -12, -32, 11, 10, (-12, -24), "GF_FRONT_CENTER", 0, 0.0, "principal,office"),
    room("GF_RECEPTION", "Reception / Enquiry", "ADMINISTRATION", "South-East", 12, -32, 11, 10, (12, -24), "GF_FRONT_CENTER", 0, 0.0, "reception,enquiry,help desk"),
    room("GF_STAFF_OFFICE", "Staff Office", "STAFF_ROOM", "South-West", -31, -32, 14, 10, (-29, -24), "GF_FRONT_WEST", 0, 0.0, "staff room,faculty room"),
    room("GF_ADMISSION", "Admission & Student Services", "SERVICE_COUNTER", "South-East", 31, -32, 14, 10, (29, -24), "GF_FRONT_EAST", 0, 0.0, "admission,bus,scholarship,fees,stationery"),
    room("GF_CLASS_L1", "Classroom L1", "CLASSROOM", "West", -33, -20, 15, 7, (-24, -20), "GF_WEST_SOUTH", 0, 0.0, "l1,class l1"),
    room("GF_CLASS_L2", "Classroom L2", "CLASSROOM", "West", -33, -12, 15, 7, (-24, -12), "GF_WEST_SOUTH", 0, 0.0, "l2,class l2"),
    room("GF_CLASS_L3", "Classroom L3", "CLASSROOM", "West", -33, -4, 15, 7, (-24, -4), "GF_WEST_CENTER", 0, 0.0, "l3,class l3"),
    room("GF_GIRLS_WC", "Girls Washroom", "WASHROOM", "West", -33, 4, 15, 7, (-24, 4), "GF_WEST_CENTER", 0, 0.0, "girls toilet,women washroom"),
    room("GF_BOYS_WC_1", "Boys Washroom 1", "WASHROOM", "West", -33, 11, 15, 6, (-24, 11), "GF_WEST_NORTH", 0, 0.0, "boys toilet,men washroom"),
    room("GF_STAIRS_1", "Staircase 1", "STAIRCASE", "West", -33, 18, 15, 6, None, None, 0, 0.0, "west stairs,stair 1"),
    room("GF_PHYSICS_LAB", "Physics Laboratory", "LABORATORY", "North-West", -34, 31, 12, 11, (-34, 24), "GF_NORTH_WEST", 0, 0.0, "physics lab"),
    room("GF_CHEMISTRY_LAB", "Chemistry Laboratory", "LABORATORY", "North-West", -22, 31, 11, 11, (-22, 24), "GF_NORTH_WEST", 0, 0.0, "chemistry lab"),
    room("GF_CIVIL_LAB", "Civil Laboratory", "LABORATORY", "North", -11, 31, 11, 11, (-11, 24), "GF_NORTH_CENTER", 0, 0.0, "civil lab", "Prototype civil engineering laboratory block."),
    room("GF_CLASS_L4", "Classroom L4", "CLASSROOM", "North", 0, 31, 9, 11, (0, 24), "GF_NORTH_CENTER", 0, 0.0, "l4,class l4"),
    room("GF_CLASS_L5", "Classroom L5", "CLASSROOM", "North", 9, 31, 9, 11, (9, 24), "GF_NORTH_CENTER", 0, 0.0, "l5,class l5"),
    room("GF_CLASS_L6", "Classroom L6", "CLASSROOM", "North", 18, 31, 9, 11, (18, 24), "GF_NORTH_EAST", 0, 0.0, "l6,class l6"),
    room("GF_DEPT_LAB", "Department Laboratory", "LABORATORY", "North-East", 28, 31, 11, 11, (28, 24), "GF_NORTH_EAST", 0, 0.0, "department lab"),
    room("GF_LIBRARY", "Central Library", "LIBRARY", "North-East", 41, 31, 15, 11, (38, 24), "GF_EXT_NORTH", 0, 0.0, "library,books,reading room"),
    room("GF_CLASS_R1", "Classroom R1", "CLASSROOM", "East", 32, -21, 14, 7, (24, -21), "GF_EAST_SOUTH", 0, 0.0, "r1,class r1"),
    room("GF_CLASS_R2", "Classroom R2", "CLASSROOM", "East", 32, -14, 14, 7, (24, -14), "GF_EAST_SOUTH", 0, 0.0, "r2,class r2"),
    room("GF_COMPUTER_LAB", "Computer Laboratory", "LABORATORY", "East", 32, -6, 14, 9, (24, -6), "GF_EAST_CENTER", 0, 0.0, "computer lab,cse lab"),
    room("GF_STAIRS_2", "Staircase 2", "STAIRCASE", "East", 32, 2, 14, 6, None, None, 0, 0.0, "east stairs,stair 2"),
    room("GF_BOYS_WC_2", "Boys Washroom 2", "WASHROOM", "East", 32, 9, 14, 6, (24, 9), "GF_EAST_NORTH", 0, 0.0, "boys toilet,men washroom"),
    room("GF_CLASS_R3", "Classroom R3", "CLASSROOM", "East", 32, 16, 14, 7, (24, 16), "GF_EAST_NORTH", 0, 0.0, "r3,class r3"),
    room("GF_CLASS_R4", "Classroom R4", "CLASSROOM", "East", 32, 23, 14, 7, (24, 23), "GF_NORTH_EAST", 0, 0.0, "r4,class r4"),
    room("GF_CLASS_R5", "Classroom R5", "CLASSROOM", "East", 46, 23, 10, 7, (38, 20), "GF_EXT_NORTH", 0, 0.0, "r5,class r5"),
    room("GF_LAB_E1", "Laboratory E1", "LABORATORY", "East Extension", 46, 13, 10, 10, (38, 13), "GF_EXT_NORTH", 0, 0.0, "lab e1"),
    room("GF_LAB_E2", "Laboratory E2", "LABORATORY", "East Extension", 46, 2, 10, 10, (38, 2), "GF_EXT_CENTER", 0, 0.0, "lab e2"),
    room("GF_LAB_E3", "Laboratory E3", "LABORATORY", "East Extension", 46, -9, 10, 10, (38, -9), "GF_EXT_SOUTH", 0, 0.0, "lab e3"),
    room("GF_COURTYARD", "Central Courtyard", "OTHER", "Central", 0, 0, 31, 31, None, None, 0, 0.0, "courtyard,garden,open space", "Open landscaped courtyard with paths, trees and seating."),

    # Second Floor Rooms (Z=7.32 m, Floor level 2) - Clearly labeled Prototype where appropriate
    room("SF_CLASS_01", "Classroom 201 (Prototype)", "CLASSROOM", "West", -33, -20, 15, 7, (-24, -20), "SF_WEST_SOUTH", 2, 7.32, "sf_class_01,class 201,201", "Second Floor Classroom 201 prototype unit.", 60, "CSE"),
    room("SF_CLASS_02", "Classroom 202 (Prototype)", "CLASSROOM", "West", -33, -12, 15, 7, (-24, -12), "SF_WEST_SOUTH", 2, 7.32, "sf_class_02,class 202,202", "Second Floor Classroom 202 prototype unit.", 60, "CSE"),
    room("SF_CLASS_03", "Classroom 203 (Prototype)", "CLASSROOM", "West", -33, -4, 15, 7, (-24, -4), "SF_WEST_CENTER", 2, 7.32, "sf_class_03,class 203,203", "Second Floor Classroom 203 prototype unit.", 60, "CSE-DS"),
    room("SF_CLASS_04", "Classroom 204 (Prototype)", "CLASSROOM", "North", 0, 31, 9, 11, (0, 24), "SF_NORTH_CENTER", 2, 7.32, "sf_class_04,class 204,204", "Second Floor Classroom 204 prototype unit.", 60, "ETC"),
    room("SF_CLASS_05", "Classroom 205 (Prototype)", "CLASSROOM", "North", 9, 31, 9, 11, (9, 24), "SF_NORTH_CENTER", 2, 7.32, "sf_class_05,class 205,205", "Second Floor Classroom 205 prototype unit.", 60, "IT"),
    room("SF_CLASS_06", "Classroom 206 (Prototype)", "CLASSROOM", "North", 18, 31, 9, 11, (18, 24), "SF_NORTH_EAST", 2, 7.32, "sf_class_06,class 206,206", "Second Floor Classroom 206 prototype unit.", 60, "CIVIL"),
    room("SF_LAB_01", "AI & Robotics Lab (Prototype)", "LABORATORY", "North-West", -34, 31, 12, 11, (-34, 24), "SF_NORTH_WEST", 2, 7.32, "sf_lab_01,ai lab,robotics lab", "Advanced AI & Robotics Laboratory prototype block.", 30, "CSE"),
    room("SF_LAB_02", "High Performance Computing Lab (Prototype)", "LABORATORY", "North-West", -22, 31, 11, 11, (-22, 24), "SF_NORTH_WEST", 2, 7.32, "sf_lab_02,hpc lab,supercomputing", "High Performance Computing Laboratory prototype block.", 30, "CSE-DS"),
    room("SF_LAB_03", "IoT & Embedded Systems Lab (Prototype)", "LABORATORY", "North-East", 28, 31, 11, 11, (28, 24), "SF_NORTH_EAST", 2, 7.32, "sf_lab_03,iot lab,embedded lab", "IoT and Embedded Systems Laboratory prototype block.", 30, "ETC"),
    room("SF_STAFF_01", "Senior Faculty Office (Prototype)", "STAFF_ROOM", "South-West", -31, -32, 14, 10, (-29, -24), "SF_FRONT_WEST", 2, 7.32, "sf_staff_01,faculty room,senior staff", "Senior Faculty & Departmental Staff Office prototype.", 20, "CSE"),
    room("SF_WASHROOM_01", "Second Floor Washrooms (Prototype)", "WASHROOM", "West", -33, 4, 15, 7, (-24, 4), "SF_WEST_CENTER", 2, 7.32, "sf_washroom_01,toilet,restroom", "Second Floor executive washrooms prototype block.", 10, None),
    room("SF_STAIRS_1", "Second Floor Staircase 1", "STAIRCASE", "West", -33, 18, 15, 6, None, None, 2, 7.32, "sf_stairs_1,staircase 1,west stairs", "Staircase 1 connecting Ground, First, and Second floors."),
    room("SF_STAIRS_2", "Second Floor Staircase 2", "STAIRCASE", "East", 32, 2, 14, 6, None, None, 2, 7.32, "sf_stairs_2,staircase 2,east stairs", "Staircase 2 connecting Ground, First, and Second floors."),
    room("SF_COURTYARD", "Central Courtyard View (Prototype)", "OTHER", "Central", 0, 0, 31, 31, None, None, 2, 7.32, "sf_courtyard,open sky,balcony", "Open-to-sky courtyard opening over central ground floor garden."),
]

QR_LOCATIONS = [
    ("GWCET-GF-MAIN-GATE", "Main Gate", "MAIN_GATE"),
    ("GWCET-GF-ENTRANCE", "Main Entrance", "GF_MAIN_ENTRANCE"),
    ("GWCET-GF-RECEPTION", "Reception", "GF_RECEPTION_DOOR"),
    ("GWCET-GF-WEST", "West Corridor", "GF_WEST_CENTER"),
    ("GWCET-GF-EAST", "East Corridor", "GF_EAST_CENTER"),
    ("GWCET-GF-NORTH", "North Corridor", "GF_NORTH_CENTER"),
    ("GWCET-GF-STAIRS-1", "Staircase 1", "GF_STAIRS_1"),
    ("GWCET-GF-STAIRS-2", "Staircase 2", "GF_STAIRS_2"),
    ("GWCET-GF-LIBRARY", "Central Library", "GF_LIBRARY_DOOR"),
    ("GWCET-GF-PHYSICS", "Physics Laboratory", "GF_PHYSICS_LAB_DOOR"),
    ("GWCET-GF-COMPUTER", "Computer Laboratory", "GF_COMPUTER_LAB_DOOR"),

    # Second Floor QR Markers
    ("GWCET-SF-STAIRS-1", "Second Floor Staircase 1", "SF_STAIRS_1"),
    ("GWCET-SF-STAIRS-2", "Second Floor Staircase 2", "SF_STAIRS_2"),
    ("GWCET-SF-CLASS-03", "Classroom 203 (SF)", "SF_CLASS_03_DOOR"),
    ("GWCET-SF-AI-LAB", "AI & Robotics Lab (SF)", "SF_LAB_01_DOOR"),
]
