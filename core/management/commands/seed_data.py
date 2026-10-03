import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from academics.models import (Batch, Department, Division, Program, Semester,
                              Subject, Syllabus, University)
from accounts.models import FacultyProfile, Guardian, StaffProfile, StudentProfile
from campus.models import Building, Campus, Floor, Room
from core.models import TimeStampedSoftDeleteModel


class Command(BaseCommand):
    help = "Seed realistic fake data for GWCET"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker("en_IN")
        Faker.seed(42)
        random.seed(42)

    def add_arguments(self, parser):
        parser.add_argument(
            "--departments", type=int, default=3, help="Number of departments"
        )
        parser.add_argument(
            "--batches", type=int, default=4, help="Number of batches per program"
        )
        parser.add_argument(
            "--students-per-div", type=int, default=60, help="Students per division"
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before seeding"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        self.stdout.write("Seeding data...")
        self.seed_university()
        self.seed_campus()
        self.seed_departments(options["departments"])
        self.seed_programs_and_batches(options["departments"], options["batches"])
        self.seed_semesters_and_divisions()
        self.seed_subjects()
        self.seed_users_and_profiles(options["students_per_div"])
        self.seed_rooms()
        self.seed_timetable()
        self.seed_fees()
        self.seed_library()
        self.stdout.write(self.style.SUCCESS("Seeding completed!"))

    def clear_data(self):
        models_to_clear = [
            "accounts.User", "academics.SubjectOffering", "academics.Syllabus",
            "academics.Subject", "academics.Division", "academics.Semester",
            "academics.Batch", "academics.Program", "academics.Department",
            "academics.University", "campus.Room", "campus.Floor", "campus.Building",
            "campus.Campus", "attendance.TimetableSlot", "fees.FeeStructure",
            "library.Book", "library.BookCategory", "notices.Notice", "notices.Event",
        ]
        for model_path in models_to_clear:
            app, model = model_path.split(".")
            Model = self.get_model(app, model)
            if Model:
                Model.objects.all().delete()

    def get_model(self, app, model):
        from django.apps import apps
        try:
            return apps.get_model(app, model)
        except LookupError:
            return None

    def seed_university(self):
        uni, _ = University.objects.get_or_create(
            code="GTU",
            defaults={
                "name": "Gujarat Technological University",
                "short_name": "GTU",
                "address": "Ahmedabad, Gujarat, India",
                "website": "https://gtu.ac.in",
                "email": "info@gtu.ac.in",
            },
        )
        self.university = uni
        self.stdout.write(f"Created university: {uni}")

    def seed_campus(self):
        campus, _ = Campus.objects.get_or_create(
            code="GWCET",
            defaults={
                "name": "Government Engineering College, Gandhinagar",
                "address": "Sector 28, Gandhinagar, Gujarat 382028",
                "latitude": Decimal("23.2239"),
                "longitude": Decimal("72.6394"),
            },
        )
        self.campus = campus

        # Main building
        building, _ = Building.objects.get_or_create(
            campus=campus,
            code="MAIN",
            defaults={
                "name": "Main Academic Building",
                "total_floors": 4,
                "year_built": 2005,
            },
        )
        self.building = building

        # Create floors
        for level in range(0, 4):
            floor, _ = Floor.objects.get_or_create(
                building=building,
                level=level,
                defaults={
                    "name": f"Floor {level}" if level > 0 else "Ground Floor",
                    "floor_height_meters": 3.66,
                    "elevation_meters": level * 3.66,
                },
            )
            setattr(self, f"floor_{level}", floor)

        self.stdout.write(f"Created campus with {building} and 4 floors")

    def seed_departments(self, count):
        dept_data = [
            ("Computer Engineering", "CE", "Computer Engineering Department"),
            ("Information Technology", "IT", "Information Technology Department"),
            ("Electronics & Communication", "EC", "E&C Engineering Department"),
            ("Mechanical Engineering", "ME", "Mechanical Engineering Department"),
            ("Civil Engineering", "CV", "Civil Engineering Department"),
            ("Electrical Engineering", "EE", "Electrical Engineering Department"),
        ]

        self.departments = []
        for i in range(min(count, len(dept_data))):
            name, code, desc = dept_data[i]
            dept, _ = Department.objects.get_or_create(
                university=self.university,
                short_code=code,
                defaults={
                    "name": name,
                    "code": f"DEPT-{code}",
                    "description": desc,
                    "established_year": 2005 + i,
                },
            )
            self.departments.append(dept)
        self.stdout.write(f"Created {len(self.departments)} departments")

    def seed_programs_and_batches(self, dept_count, batch_count):
        self.programs = []
        self.batches = []
        for dept in self.departments:
            program, _ = Program.objects.get_or_create(
                department=dept,
                code="BE",
                defaults={
                    "name": f"Bachelor of Engineering in {dept.name}",
                    "short_name": f"BE {dept.short_code}",
                    "level": Program.Level.UG,
                    "duration_years": 4,
                    "total_semesters": 8,
                    "credits_required": 176,
                    "intake_capacity": 120,
                },
            )
            self.programs.append(program)

            current_year = timezone.now().year
            for i in range(batch_count):
                year_start = current_year - batch_count + i + 1
                batch, _ = Batch.objects.get_or_create(
                    program=program,
                    academic_year_start=year_start,
                    defaults={
                        "academic_year_end": year_start + 4,
                        "batch_code": f"{year_start}-{year_start+4}",
                        "strength": 120,
                    },
                )
                self.batches.append(batch)
        self.stdout.write(f"Created {len(self.programs)} programs and {len(self.batches)} batches")

    def seed_semesters_and_divisions(self):
        self.divisions = []
        for batch in self.batches:
            for sem_num in range(1, 9):
                sem, _ = Semester.objects.get_or_create(
                    batch=batch,
                    number=sem_num,
                    defaults={
                        "name": f"Semester {sem_num}",
                        "start_date": date(batch.academic_year_start + (sem_num-1)//2, 7 if sem_num % 2 == 1 else 1, 1),
                        "end_date": date(batch.academic_year_start + sem_num//2, 12 if sem_num % 2 == 1 else 6, 30),
                        "is_current": sem_num == 8,
                    },
                )
                # 2 divisions per semester
                for div_name in ["A", "B"]:
                    div, _ = Division.objects.get_or_create(
                        semester=sem,
                        name=div_name,
                        defaults={"capacity": 60},
                    )
                    self.divisions.append(div)
        self.stdout.write(f"Created semesters and {len(self.divisions)} divisions")

    def seed_subjects(self):
        subject_templates = {
            "CE": [
                ("CE101", "Programming Fundamentals", Subject.Type.THEORY, 4),
                ("CE102", "Data Structures", Subject.Type.THEORY, 4),
                ("CE103", "Digital Logic Design", Subject.Type.THEORY, 3),
                ("CE104", "Computer Organization", Subject.Type.THEORY, 4),
                ("CE201", "Database Management Systems", Subject.Type.THEORY, 4),
                ("CE202", "Operating Systems", Subject.Type.THEORY, 4),
                ("CE203", "Computer Networks", Subject.Type.THEORY, 4),
                ("CE204", "Software Engineering", Subject.Type.THEORY, 3),
                ("CE301", "Machine Learning", Subject.Type.THEORY, 4),
                ("CE302", "Compiler Design", Subject.Type.THEORY, 3),
                ("CEL101", "Programming Lab", Subject.Type.PRACTICAL, 2),
                ("CEL102", "Data Structures Lab", Subject.Type.PRACTICAL, 2),
                ("CEL201", "DBMS Lab", Subject.Type.PRACTICAL, 2),
                ("CEL202", "OS & Networks Lab", Subject.Type.PRACTICAL, 2),
            ],
            "IT": [
                ("IT101", "Web Technologies", Subject.Type.THEORY, 3),
                ("IT102", "Object Oriented Programming", Subject.Type.THEORY, 4),
                ("IT103", "Discrete Mathematics", Subject.Type.THEORY, 3),
                ("IT201", "Computer Networks", Subject.Type.THEORY, 4),
                ("IT202", "Database Systems", Subject.Type.THEORY, 4),
                ("IT203", "Software Testing", Subject.Type.THEORY, 3),
                ("ITL101", "Web Tech Lab", Subject.Type.PRACTICAL, 2),
                ("ITL102", "OOP Lab", Subject.Type.PRACTICAL, 2),
            ],
            "EC": [
                ("EC101", "Electronic Devices", Subject.Type.THEORY, 4),
                ("EC102", "Signals & Systems", Subject.Type.THEORY, 4),
                ("EC103", "Digital Electronics", Subject.Type.THEORY, 3),
                ("EC201", "Analog Communication", Subject.Type.THEORY, 4),
                ("EC202", "Microcontrollers", Subject.Type.THEORY, 3),
                ("EC203", "Digital Communication", Subject.Type.THEORY, 4),
                ("ECL101", "Electronics Lab", Subject.Type.PRACTICAL, 2),
                ("ECL102", "Digital Electronics Lab", Subject.Type.PRACTICAL, 2),
            ],
        }

        self.subjects = []
        for dept in self.departments:
            templates = subject_templates.get(dept.short_code, [])
            for code, name, subj_type, credits in templates:
                subj, _ = Subject.objects.get_or_create(
                    department=dept,
                    code=code,
                    defaults={
                        "name": name,
                        "short_name": code,
                        "subject_type": subj_type,
                        "credits": credits,
                        "theory_hours": 3 if subj_type == Subject.Type.THEORY else 0,
                        "practical_hours": 3 if subj_type == Subject.Type.PRACTICAL else 0,
                    },
                )
                self.subjects.append(subj)

                # Create syllabus
                Syllabus.objects.get_or_create(
                    subject=subj,
                    version="2024",
                    defaults={
                        "effective_from": date(2024, 1, 1),
                        "topics": [{"unit": i, "title": f"Unit {i}", "hours": 8} for i in range(1, 6)],
                        "is_current": True,
                    },
                )
        self.stdout.write(f"Created {len(self.subjects)} subjects with syllabi")

    def seed_users_and_profiles(self, students_per_div):
        from accounts.models import User

        # Create faculty users
        designations = [
            ("Prof.", "PROFESSOR"),
            ("Dr.", "ASSOCIATE_PROF"),
            ("Mr./Ms.", "ASSISTANT_PROF"),
        ]

        for i, dept in enumerate(self.departments):
            # HOD
            hod_user = User.objects.create_user(
                username=f"hod_{dept.short_code.lower()}",
                email=f"hod.{dept.short_code.lower()}@gwcet.ac.in",
                password="gwcet123",
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                role=User.Role.HOD,
                phone=self.fake.phone_number()[:15],
            )
            FacultyProfile.objects.create(
                user=hod_user,
                employee_id=f"EMP{1000+i}",
                designation="HOD",
                department=dept,
                qualifications=[{"degree": "Ph.D", "field": dept.name, "year": 2005}],
                experience_years=15 + i,
                joining_date=date(2008, 7, 1),
                specialization=dept.name,
            )
            dept.hod = hod_user.faculty_profile
            dept.save()

            # Faculty
            for j in range(4):
                prefix, desig = random.choice(designations)
                fac_user = User.objects.create_user(
                    username=f"fac_{dept.short_code.lower()}{j}",
                    email=f"fac.{dept.short_code.lower()}{j}@gwcet.ac.in",
                    password="gwcet123",
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    role=User.Role.FACULTY,
                    phone=self.fake.phone_number()[:15],
                )
                FacultyProfile.objects.create(
                    user=fac_user,
                    employee_id=f"EMP{2000+i*10+j}",
                    designation=desig,
                    department=dept,
                    qualifications=[{"degree": "M.Tech", "field": dept.name, "year": 2010+j}],
                    experience_years=5 + j,
                    joining_date=date(2015+j, 7, 1),
                    specialization=dept.name,
                )

        # Create students
        student_count = 0
        for division in self.divisions:
            for k in range(students_per_div):
                student_count += 1
                stu_user = User.objects.create_user(
                    username=f"stu_{division.semester.batch.batch_code.replace('-','')}_{division.name}_{k:03d}",
                    email=f"stu{student_count}@gwcet.ac.in",
                    password="gwcet123",
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    role=User.Role.STUDENT,
                    phone=self.fake.phone_number()[:15],
                )
                batch_year = division.semester.batch.academic_year_start
                enrollment = f"{division.semester.batch.program.department.short_code}{batch_year%100}{k+1:04d}"
                roll = f"{batch_year%100}{division.semester.batch.program.department.short_code}{division.name}{k+1:03d}"
                StudentProfile.objects.create(
                    user=stu_user,
                    enrollment_number=enrollment,
                    roll_number=roll,
                    admission_year=batch_year,
                    category=random.choice(["GEN", "OBC", "SC", "ST", "EWS"]),
                    blood_group=random.choice(["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"]),
                    current_semester=division.semester,
                    division=division,
                )
        self.stdout.write(f"Created faculty and {student_count} students")

        # Staff
        for i in range(5):
            staff_user = User.objects.create_user(
                username=f"staff_{i}",
                email=f"staff{i}@gwcet.ac.in",
                password="gwcet123",
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                role=User.Role.STAFF,
            )
            StaffProfile.objects.create(
                user=staff_user,
                employee_id=f"STF{1000+i}",
                designation=["Clerk", "Accountant", "Librarian", "Admin Assistant", "Technician"][i],
                joining_date=date(2010+i, 1, 1),
            )

        # Admin user
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@gwcet.ac.in",
            password="admin123",
            role=User.Role.ADMIN,
        )
        self.stdout.write("Created admin user (admin/admin123)")

    def seed_rooms(self):
        room_types_by_floor = {
            0: [Room.RoomType.ADMIN_OFFICE, Room.RoomType.PRINCIPAL_OFFICE, Room.RoomType.STAFF_ROOM,
                Room.RoomType.CLASSROOM, Room.RoomType.LABORATORY, Room.RoomType.LIBRARY],
            1: [Room.RoomType.CLASSROOM, Room.RoomType.LABORATORY, Room.RoomType.FACULTY_OFFICE],
            2: [Room.RoomType.CLASSROOM, Room.RoomType.LABORATORY, Room.RoomType.FACULTY_OFFICE],
            3: [Room.RoomType.CLASSROOM, Room.RoomType.LABORATORY, Room.RoomType.SENATE_HALL],
        }

        room_counter = 0
        for level in range(4):
            floor = getattr(self, f"floor_{level}")
            types = room_types_by_floor[level]
            for idx, rtype in enumerate(types):
                room_counter += 1
                dept = random.choice(self.departments) if rtype in [Room.RoomType.CLASSROOM, Room.RoomType.LABORATORY, Room.RoomType.FACULTY_OFFICE] else None
                Room.objects.get_or_create(
                    room_code=f"{self.building.code}{level}{idx+1:02d}",
                    defaults={
                        "floor": floor,
                        "department": dept,
                        "name": f"{rtype.label} {idx+1}",
                        "room_type": rtype,
                        "capacity": 60 if rtype == Room.RoomType.CLASSROOM else (30 if rtype == Room.RoomType.LABORATORY else 10),
                        "x": idx * 10.0,
                        "y": level * 5.0,
                        "z": level * 3.66,
                        "width": 8.0,
                        "length": 12.0,
                        "has_projector": rtype == Room.RoomType.CLASSROOM,
                        "has_ac": rtype in [Room.RoomType.COMPUTER_LAB, Room.RoomType.HOD_OFFICE, Room.RoomType.PRINCIPAL_OFFICE],
                    },
                )
        self.stdout.write(f"Created {room_counter} rooms")

    def seed_timetable(self):
        from attendance.models import TimetableSlot
        from academics.models import SubjectOffering

        # Create subject offerings and timetable slots
        for division in self.divisions:
            sem_subjects = [s for s in self.subjects if s.department == division.semester.batch.program.department]
            selected = random.sample(sem_subjects, min(6, len(sem_subjects)))
            for subj in selected:
                faculty = division.semester.batch.program.department.faculty.filter(is_active=True).first()
                offering, _ = SubjectOffering.objects.get_or_create(
                    semester=division.semester,
                    subject=subj,
                    division=division,
                    defaults={"faculty": faculty},
                )
                # Create 2-3 slots per week
                for day in range(5):  # Mon-Fri
                    if random.random() > 0.5:
                        start = time(9 + random.randint(0, 4), 0)
                        end = time(start.hour + 1, 0)
                        room = Room.objects.filter(room_type=Room.RoomType.CLASSROOM, is_active=True).first()
                        TimetableSlot.objects.get_or_create(
                            subject_offering=offering,
                            day=day,
                            start_time=start,
                            end_time=end,
                            defaults={"room": room, "effective_from": date.today()},
                        )
        self.stdout.write("Created timetable slots")

    def seed_fees(self):
        for batch in self.batches:
            for sem in batch.semesters.all():
                fee_types = [
                    (FeeStructure.FeeType.TUITION, "Tuition Fee", 35000),
                    (FeeStructure.FeeType.LAB, "Laboratory Fee", 5000),
                    (FeeStructure.FeeType.LIBRARY, "Library Fee", 2000),
                    (FeeStructure.FeeType.EXAM, "Examination Fee", 3000),
                    (FeeStructure.FeeType.DEVELOPMENT, "Development Fee", 10000),
                ]
                for ftype, name, amount in fee_types:
                    FeeStructure.objects.get_or_create(
                        program=batch.program,
                        batch=batch,
                        semester=sem,
                        fee_type=ftype,
                        defaults={
                            "name": name,
                            "amount": Decimal(str(amount)),
                            "due_date": date(sem.start_date.year, sem.start_date.month, 15),
                            "late_fine_per_day": Decimal("50"),
                            "max_late_fine": Decimal("2000"),
                        },
                    )
        self.stdout.write("Created fee structures")

    def seed_library(self):
        categories = [
            ("Computer Science", "CS"),
            ("Electronics", "EC"),
            ("Mechanical", "ME"),
            ("Mathematics", "MA"),
            ("Physics", "PH"),
            ("Reference", "REF"),
        ]
        for name, code in categories:
            BookCategory.objects.get_or_create(code=code, defaults={"name": name})

        for subj in self.subjects[:10]:
            cat = BookCategory.objects.filter(code=subj.department.short_code).first()
            book, _ = Book.objects.get_or_create(
                isbn=f"978{random.randint(1000000000, 9999999999)}",
                defaults={
                    "title": f"{subj.name} - Textbook",
                    "authors": [{"name": self.fake.name(), "role": "author"}],
                    "publisher": self.fake.company(),
                    "publication_year": random.randint(2018, 2024),
                    "edition": f"{random.randint(1, 5)}th",
                    "category": cat,
                    "total_copies": 5,
                    "available_copies": 5,
                    "location": f"{cat.code}-{random.randint(1, 10)}",
                    "price": Decimal(str(random.randint(500, 3000))),
                },
            )
            for copy_num in range(1, 6):
                BookCopy.objects.get_or_create(
                    book=book,
                    copy_number=copy_num,
                    defaults={
                        "accession_number": f"ACC{book.id:06d}{copy_num}",
                        "barcode": f"BAR{book.id:06d}{copy_num}",
                        "acquired_date": date.today() - timedelta(days=random.randint(0, 365)),
                    },
                )
        self.stdout.write("Seeded library books")

    def get_model(self, app, model):
        from django.apps import apps
        try:
            return apps.get_model(app, model)
        except LookupError:
            return None


# Need to import FeeStructure at top
from fees.models import FeeStructure