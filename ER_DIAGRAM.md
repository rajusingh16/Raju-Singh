# GWCET LiveTracker - Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    %% CORE
    TIMESTAMPED ||--o{ TIMESTAMPED_SOFTDELETE : extends
    SOFTDELETE ||--o{ TIMESTAMPED_SOFTDELETE : extends

    %% ACCOUNTS
    USER ||--|| STUDENT_PROFILE : "has"
    USER ||--|| FACULTY_PROFILE : "has"
    USER ||--|| STAFF_PROFILE : "has"
    USER ||--|| GUARDIAN : "is guardian of"
    GUARDIAN ||--|| STUDENT_PROFILE : "guards"

    USER {
        string id PK
        string email UK
        string username
        string role
        string phone
        boolean is_verified
        boolean is_deleted
        datetime created_at
        datetime updated_at
    }

    STUDENT_PROFILE {
        string id PK
        string user_id FK
        string enrollment_number UK
        string roll_number UK
        int admission_year
        string category
        string blood_group
        int guardian_id FK
        int current_semester_id FK
        int division_id FK
        boolean is_deleted
    }

    FACULTY_PROFILE {
        string id PK
        string user_id FK
        string employee_id UK
        string designation
        int department_id FK
        json qualifications
        int experience_years
        date joining_date
        string specialization
        boolean is_active
    }

    STAFF_PROFILE {
        string id PK
        string user_id FK
        string employee_id UK
        string designation
        int department_id FK
        date joining_date
        boolean is_active
    }

    GUARDIAN {
        string id PK
        string user_id FK
        string name
        string relationship
        string phone
        string email
        text address
        string occupation
        decimal annual_income
    }

    %% ACADEMICS
    UNIVERSITY ||--o{ DEPARTMENT : "has"
    DEPARTMENT ||--o{ PROGRAM : "offers"
    PROGRAM ||--o{ BATCH : "has"
    BATCH ||--o{ SEMESTER : "contains"
    SEMESTER ||--o{ DIVISION : "has"
    DIVISION ||--o{ STUDENT_PROFILE : "enrolled_in"
    DEPARTMENT ||--o{ SUBJECT : "teaches"
    SUBJECT ||--o{ SYLLABUS : "has"
    SEMESTER ||--o{ SUBJECT_OFFERING : "offers"
    SUBJECT ||--o{ SUBJECT_OFFERING : "offered_as"
    DIVISION ||--o{ SUBJECT_OFFERING : "has"
    FACULTY_PROFILE ||--o{ SUBJECT_OFFERING : "teaches"

    UNIVERSITY {
        string id PK
        string name
        string short_name UK
        string code UK
        text address
        string website
        string email
        string phone
        boolean is_active
    }

    DEPARTMENT {
        string id PK
        int university_id FK
        string name
        string short_code UK
        string code UK
        text description
        int hod_id FK
        int established_year
        boolean is_active
    }

    PROGRAM {
        string id PK
        int department_id FK
        string name
        string short_name
        string code
        string level
        int duration_years
        int total_semesters
        int credits_required
        int intake_capacity
        boolean is_active
    }

    BATCH {
        string id PK
        int program_id FK
        int academic_year_start
        int academic_year_end
        string batch_code
        int strength
        boolean is_active
    }

    SEMESTER {
        string id PK
        int batch_id FK
        int number
        string name
        date start_date
        date end_date
        boolean is_current
        boolean is_active
    }

    DIVISION {
        string id PK
        int semester_id FK
        string name
        int capacity
        int class_advisor_id FK
        boolean is_active
    }

    SUBJECT {
        string id PK
        int department_id FK
        string code UK
        string name
        string short_name
        string subject_type
        int credits
        int theory_hours
        int practical_hours
        int tutorial_hours
        text description
        boolean is_active
    }

    SYLLABUS {
        string id PK
        int subject_id FK
        string version
        date effective_from
        date effective_to
        json topics
        json reference_books
        boolean is_current
    }

    SUBJECT_OFFERING {
        string id PK
        int semester_id FK
        int subject_id FK
        int division_id FK
        int faculty_id FK
        boolean is_elective
        string elective_group
        boolean is_active
    }

    %% CAMPUS
    CAMPUS ||--o{ BUILDING : "contains"
    BUILDING ||--o{ FLOOR : "has"
    FLOOR ||--o{ ROOM : "contains"
    DEPARTMENT ||--o{ ROOM : "uses"
    ROOM ||--o{ ROOM_BOOKING : "booked_as"
    USER ||--o{ ROOM_BOOKING : "books"
    SUBJECT_OFFERING ||--o{ ROOM_BOOKING : "uses"

    CAMPUS {
        string id PK
        string name
        string code UK
        text description
        text address
        decimal latitude
        decimal longitude
        boolean is_active
    }

    BUILDING {
        string id PK
        int campus_id FK
        string name
        string code
        text description
        decimal latitude
        decimal longitude
        int total_floors
        int year_built
        boolean is_active
    }

    FLOOR {
        string id PK
        int building_id FK
        int level
        string name
        float floor_height_meters
        float elevation_meters
        string layout_image
        boolean is_active
    }

    ROOM {
        string id PK
        int floor_id FK
        int department_id FK
        string room_code UK
        string name
        string room_type
        int capacity
        float x
        float y
        float z
        float width
        float length
        float height
        json layout
        boolean has_projector
        boolean has_ac
        boolean has_whiteboard
        boolean has_smart_board
        int computers_count
        boolean is_accessible
        boolean requires_keycard
        boolean is_active
        text maintenance_note
    }

    ROOM_BOOKING {
        string id PK
        int room_id FK
        int booked_by_id FK
        int subject_offering_id FK
        string title
        text description
        datetime start_time
        datetime end_time
        string status
        boolean recurring
        string recurrence_rule
        int approved_by_id FK
        datetime approved_at
    }

    %% ATTENDANCE
    SUBJECT_OFFERING ||--o{ TIMETABLE_SLOT : "scheduled_as"
    ROOM ||--o{ TIMETABLE_SLOT : "hosts"
    TIMETABLE_SLOT ||--o{ ATTENDANCE_RECORD : "records"
    STUDENT_PROFILE ||--o{ ATTENDANCE_RECORD : "has"
    USER ||--o{ ATTENDANCE_RECORD : "marked_by"
    STUDENT_PROFILE ||--o{ LEAVE_REQUEST : "requests"
    USER ||--o{ LEAVE_REQUEST : "reviews"
    STUDENT_PROFILE ||--o{ ATTENDANCE_SUMMARY : "summarized_in"
    SUBJECT_OFFERING ||--o{ ATTENDANCE_SUMMARY : "summarized_for"

    TIMETABLE_SLOT {
        string id PK
        int subject_offering_id FK
        int day
        time start_time
        time end_time
        int room_id FK
        string slot_type
        boolean is_recurring
        date effective_from
        date effective_to
        boolean is_active
    }

    ATTENDANCE_RECORD {
        string id PK
        int timetable_slot_id FK
        int student_id FK
        date date
        string status
        int marked_by_id FK
        datetime marked_at
        text notes
        int minutes_late
    }

    LEAVE_REQUEST {
        string id PK
        int student_id FK
        string leave_type
        date start_date
        date end_date
        text reason
        string status
        datetime applied_at
        int reviewed_by_id FK
        datetime reviewed_at
        text review_notes
    }

    ATTENDANCE_SUMMARY {
        string id PK
        int student_id FK
        int subject_offering_id FK
        date month
        int total_sessions
        int attended_sessions
        decimal percentage
    }

    %% EXAMS
    SUBJECT_OFFERING ||--o{ EXAM : "has"
    ROOM ||--o{ EXAM : "conducted_in"
    FACULTY_PROFILE ||--o{ EXAM : "invigilates"
    EXAM ||--o{ EXAM_RESULT : "produces"
    STUDENT_PROFILE ||--o{ EXAM_RESULT : "gets"
    USER ||--o{ EXAM_RESULT : "graded_by"
    SUBJECT_OFFERING ||--o{ GRADE : "graded_as"
    STUDENT_PROFILE ||--o{ GRADE : "receives"
    USER ||--o{ GRADE : "calculated_by"
    STUDENT_PROFILE ||--o{ SEMESTER_RESULT : "achieves"
    SEMESTER ||--o{ SEMESTER_RESULT : "summarized_in"
    USER ||--o{ SEMESTER_RESULT : "calculated_by"

    EXAM {
        string id PK
        int subject_offering_id FK
        string exam_type
        string name
        int max_marks
        decimal weightage
        date exam_date
        time start_time
        time end_time
        int room_id FK
        text instructions
        boolean is_published
        boolean is_active
    }

    EXAM_RESULT {
        string id PK
        int exam_id FK
        int student_id FK
        decimal marks_obtained
        int graded_by_id FK
        datetime graded_at
        boolean is_absent
        boolean is_malpractice
        text remarks
        boolean re_evaluation_requested
        decimal re_evaluation_marks
    }

    GRADE {
        string id PK
        int subject_offering_id FK
        int student_id FK
        string grade
        decimal grade_points
        decimal total_marks
        decimal percentage
        boolean is_final
        datetime calculated_at
        int calculated_by_id FK
    }

    SEMESTER_RESULT {
        string id PK
        int student_id FK
        int semester_id FK
        decimal sgpa
        decimal cgpa
        int total_credits
        int earned_credits
        int backlogs
        boolean is_passed
        int rank
        int total_students
        datetime calculated_at
        int calculated_by_id FK
    }

    %% FEES
    PROGRAM ||--o{ FEE_STRUCTURE : "defines"
    BATCH ||--o{ FEE_STRUCTURE : "applies_to"
    SEMESTER ||--o{ FEE_STRUCTURE : "for"
    FEE_STRUCTURE ||--o{ FEE_PAYMENT : "paid_via"
    STUDENT_PROFILE ||--o{ FEE_PAYMENT : "makes"
    USER ||--o{ FEE_PAYMENT : "received_by"
    FEE_PAYMENT ||--|| FEE_RECEIPT : "generates"
    STUDENT_PROFILE ||--o{ FEE_DUE : "owes"
    FEE_STRUCTURE ||--o{ FEE_DUE : "tracks"
    STUDENT_PROFILE ||--o{ SCHOLARSHIP : "receives"

    FEE_STRUCTURE {
        string id PK
        int program_id FK
        int batch_id FK
        int semester_id FK
        string fee_type
        string name
        decimal amount
        boolean is_mandatory
        date due_date
        decimal late_fine_per_day
        decimal max_late_fine
        text description
        boolean is_active
    }

    FEE_PAYMENT {
        string id PK
        int student_id FK
        int fee_structure_id FK
        decimal amount_paid
        decimal late_fine_paid
        string payment_mode
        string transaction_id UK
        datetime payment_date
        string status
        json payment_gateway_response
        int received_by_id FK
        string receipt_number UK
        text remarks
    }

    FEE_RECEIPT {
        string id PK
        int payment_id FK
        string receipt_number UK
        datetime generated_at
        int generated_by_id FK
        string pdf_file
        boolean is_sent
        datetime sent_at
    }

    FEE_DUE {
        string id PK
        int student_id FK
        int fee_structure_id FK
        decimal total_amount
        decimal paid_amount
        decimal late_fine
        decimal waiver_amount
        decimal balance
        boolean is_cleared
        datetime cleared_at
        datetime last_payment_date
    }

    SCHOLARSHIP {
        string id PK
        int student_id FK
        string name
        string scholarship_type
        decimal amount
        string academic_year
        date sanctioned_date
        date disbursed_date
        boolean is_disbursed
        string sanction_order
        text remarks
    }

    %% NOTICES
    USER ||--o{ NOTICE : "authors"
    DEPARTMENT ||--o{ NOTICE : "targets"
    BATCH ||--o{ NOTICE : "targets"
    DIVISION ||--o{ NOTICE : "targets"
    USER ||--o{ NOTICE : "read_by"
    USER ||--o{ EVENT : "organizes"
    DEPARTMENT ||--o{ EVENT : "organizes"
    ROOM ||--o{ EVENT : "held_at"
    USER ||--o{ EVENT : "registers_for"

    NOTICE {
        string id PK
        string title
        text content
        string priority
        string audience
        string attachment
        boolean is_published
        datetime published_at
        datetime expires_at
        int author_id FK
        boolean is_pinned
    }

    NOTICE_READ {
        string id PK
        int notice_id FK
        int user_id FK
        datetime read_at
    }

    EVENT {
        string id PK
        string title
        text description
        string event_type
        datetime start_datetime
        datetime end_datetime
        int venue_id FK
        string venue_custom
        int organizer_id FK
        int organizing_dept_id FK
        boolean requires_registration
        int max_participants
        datetime registration_deadline
        boolean is_public
        string target_audience
        boolean is_cancelled
        text cancellation_reason
    }

    EVENT_REGISTRATION {
        string id PK
        int event_id FK
        int user_id FK
        string status
        datetime registered_at
        datetime confirmed_at
        datetime attended_at
    }

    %% LIBRARY
    BOOK_CATEGORY ||--o{ BOOK : "categorizes"
    BOOK_CATEGORY ||--o{ BOOK_CATEGORY : "parent_of"
    BOOK ||--o{ BOOK_COPY : "has_copies"
    BOOK_COPY ||--o{ ISSUE_RECORD : "issued_as"
    USER ||--o{ ISSUE_RECORD : "issued_to"
    USER ||--o{ ISSUE_RECORD : "issued_by"
    ISSUE_RECORD ||--|| RETURN_RECORD : "returned_via"
    USER ||--o{ RETURN_RECORD : "returned_by"
    USER ||--o{ RETURN_RECORD : "received_by"
    BOOK ||--o{ BOOK_RESERVATION : "reserved_as"
    USER ||--o{ BOOK_RESERVATION : "reserves"
    USER ||--|| LIBRARY_FINE : "has_fines"

    BOOK_CATEGORY {
        string id PK
        string name UK
        string code UK
        text description
        int parent_id FK
    }

    BOOK {
        string id PK
        string isbn UK
        string title
        string subtitle
        json authors
        string publisher
        int publication_year
        string edition
        int category_id FK
        json subject_tags
        string language
        int pages
        int total_copies
        int available_copies
        string location
        string status
        decimal price
        string cover_image
        text description
        text keywords
    }

    BOOK_COPY {
        string id PK
        int book_id FK
        int copy_number
        string accession_number UK
        string barcode UK
        string status
        string condition
        date acquired_date
        string acquired_from
        decimal cost
        string current_location
    }

    ISSUE_RECORD {
        string id PK
        int book_copy_id FK
        int issued_to_id FK
        string issue_type
        datetime issued_at
        datetime due_date
        int issued_by_id FK
        int renewal_count
        int max_renewals
        datetime last_renewed_at
        boolean is_returned
        datetime returned_at
        int returned_to_id FK
        decimal fine_amount
        boolean fine_paid
        text notes
    }

    RETURN_RECORD {
        string id PK
        int issue_record_id FK
        datetime returned_at
        int returned_by_id FK
        int received_by_id FK
        string condition_on_return
        text damage_description
        decimal damage_fine
        decimal late_fine
        decimal total_fine
        boolean fine_paid
        string payment_reference
        text remarks
    }

    BOOK_RESERVATION {
        string id PK
        int book_id FK
        int user_id FK
        datetime reserved_at
        datetime expires_at
        boolean is_fulfilled
        datetime fulfilled_at
        datetime cancelled_at
        int position_in_queue
    }

    LIBRARY_FINE {
        string id PK
        int user_id FK
        decimal total_fine
        decimal paid_amount
        decimal balance
        boolean is_cleared
        datetime last_updated
    }

    %% INDOOR NAV (legacy tracker)
    CAMPUS ||--o{ NAV_FLOOR : "has"
    NAV_FLOOR ||--o{ NAVIGATION_POINT : "contains"
    NAVIGATION_POINT ||--o{ NAVIGATION_EDGE : "connects_from"
    NAVIGATION_POINT ||--o{ NAVIGATION_EDGE : "connects_to"
    NAVIGATION_POINT ||--|| QR_LOCATION : "has"
    USER ||--|| USER_LOCATION : "located_at"
    NAV_FLOOR ||--o{ USER_LOCATION : "on"
    NAVIGATION_POINT ||--o{ USER_LOCATION : "near"
    USER ||--o{ LOCATION_SHARE : "shares_as_owner"
    USER ||--o{ LOCATION_SHARE : "shares_as_viewer"

    NAV_FLOOR {
        string id PK
        int campus_id FK
        int level
        string name
        float elevation
        float floor_height
        string model_file
    }

    NAVIGATION_POINT {
        string id PK
        int floor_id FK
        string code UK
        string name
        string point_type
        float x
        float y
        float z
        boolean is_accessible
    }

    NAVIGATION_EDGE {
        string id PK
        int start_point_id FK
        int end_point_id FK
        float distance
        boolean accessible
        boolean stairs
        boolean lift
        boolean is_closed
    }

    QR_LOCATION {
        string id PK
        string code UK
        string label
        int navigation_point_id FK
    }

    USER_LOCATION {
        string id PK
        int user_id FK
        int floor_id FK
        int navigation_point_id FK
        float x
        float y
        float z
        datetime updated_at
    }

    LOCATION_SHARE {
        string id PK
        int owner_id FK
        int viewer_id FK
        datetime start_time
        datetime expiry_time
        boolean active
    }
```