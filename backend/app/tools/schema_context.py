from __future__ import annotations

SCHEMA_DESCRIPTION = """\
## Karnataka Police FIR Database Schema

### Tables and Columns

#### case_master (main case table)
- case_id INTEGER PRIMARY KEY
- case_no VARCHAR(50) UNIQUE — e.g. "KA-2024-0001"
- crime_no VARCHAR(50) UNIQUE — e.g. "Cr.No.123/2024"
- crime_registered_date VARCHAR(20) — date FIR was registered
- police_person_id INTEGER FK → employee.employee_id
- police_station_id INTEGER FK → unit.unit_id
- case_category_id INTEGER FK → case_category.case_category_id
- gravity_offence_id INTEGER FK → gravity_offence.gravity_offence_id
- crime_major_head_id INTEGER FK → crime_head.crime_head_id
- crime_minor_head_id INTEGER
- case_status_id INTEGER FK → case_status_master.case_status_id
- court_id INTEGER FK → court.court_id
- incident_from_date VARCHAR(20) — incident start date
- incident_to_date VARCHAR(20) — incident end date
- latitude FLOAT
- longitude FLOAT
- brief_facts TEXT — narrative of the incident

#### complainant_details
- complainant_id INTEGER PRIMARY KEY
- case_id INTEGER FK → case_master.case_id
- name VARCHAR(150)
- age INTEGER
- gender VARCHAR(10)
- address TEXT
- phone VARCHAR(20)

#### victim
- victim_id INTEGER PRIMARY KEY
- case_id INTEGER FK → case_master.case_id
- name VARCHAR(150)
- age INTEGER
- gender VARCHAR(10)
- address TEXT
- caste_id INTEGER
- religion_id INTEGER
- occupation_id INTEGER

#### accused
- accused_id INTEGER PRIMARY KEY
- case_id INTEGER FK → case_master.case_id
- name VARCHAR(150)
- age INTEGER
- gender VARCHAR(10)
- address TEXT
- caste_id INTEGER
- religion_id INTEGER
- occupation_id INTEGER

#### arrest_surrender
- arrest_id INTEGER PRIMARY KEY
- case_id INTEGER FK → case_master.case_id
- accused_name VARCHAR(150)
- arrest_date VARCHAR(20)
- surrender_date VARCHAR(20)
- arrested_by VARCHAR(150)

#### act_section_association
- id INTEGER PRIMARY KEY
- case_id INTEGER FK → case_master.case_id
- act_id INTEGER
- section_id INTEGER

#### chargesheet_details
- chargesheet_id INTEGER PRIMARY KEY
- case_id INTEGER FK → case_master.case_id
- chargesheet_date VARCHAR(20)
- investigating_officer VARCHAR(150)
- chargesheet_number VARCHAR(50)

#### state
- state_id INTEGER PRIMARY KEY
- state_name VARCHAR(100)

#### district
- district_id INTEGER PRIMARY KEY
- district_name VARCHAR(100)
- state_id INTEGER

#### unit (police stations / units)
- unit_id INTEGER PRIMARY KEY
- unit_name VARCHAR(150)
- unit_type VARCHAR(50)
- district_id INTEGER

#### court
- court_id INTEGER PRIMARY KEY
- court_name VARCHAR(200)
- court_type VARCHAR(50)

#### rank
- rank_id INTEGER PRIMARY KEY
- rank_name VARCHAR(100)

#### designation
- designation_id INTEGER PRIMARY KEY
- designation_name VARCHAR(100)

#### employee
- employee_id INTEGER PRIMARY KEY
- name VARCHAR(150)
- badge_number VARCHAR(50)
- rank_id INTEGER
- designation_id INTEGER
- unit_id INTEGER FK → unit.unit_id

#### case_category
- case_category_id INTEGER PRIMARY KEY
- category_name VARCHAR(150)

#### gravity_offence
- gravity_offence_id INTEGER PRIMARY KEY
- gravity_name VARCHAR(100)

#### case_status_master
- case_status_id INTEGER PRIMARY KEY
- status_name VARCHAR(100)

#### crime_head
- crime_head_id INTEGER PRIMARY KEY
- head_name VARCHAR(200)

#### crime_sub_head
- crime_sub_head_id INTEGER PRIMARY KEY
- sub_head_name VARCHAR(200)
- crime_head_id INTEGER

#### act
- act_id INTEGER PRIMARY KEY
- act_name TEXT

#### section
- section_id INTEGER PRIMARY KEY
- section_number VARCHAR(50)
- description TEXT
- act_id INTEGER

#### crime_head_act_section
- id INTEGER PRIMARY KEY
- crime_head_id INTEGER
- act_id INTEGER
- section_id INTEGER

#### caste_master
- caste_id INTEGER PRIMARY KEY
- caste_name VARCHAR(100)

#### religion_master
- religion_id INTEGER PRIMARY KEY
- religion_name VARCHAR(100)

#### occupation_master
- occupation_id INTEGER PRIMARY KEY
- occupation_name VARCHAR(100)

### Key Relationships
- case_master.police_person_id → employee.employee_id (investigating officer)
- case_master.police_station_id → unit.unit_id (police station)
- case_master.case_category_id → case_category.case_category_id
- case_master.gravity_offence_id → gravity_offence.gravity_offence_id
- case_master.crime_major_head_id → crime_head.crime_head_id
- case_master.case_status_id → case_status_master.case_status_id
- case_master.court_id → court.court_id
- complainant_details.case_id → case_master.case_id
- victim.case_id → case_master.case_id
- accused.case_id → case_master.case_id
- arrest_surrender.case_id → case_master.case_id
- act_section_association.case_id → case_master.case_id
- chargesheet_details.case_id → case_master.case_id
- unit.district_id → district.district_id
- district.state_id → state.state_id
- employee.unit_id → unit.unit_id
- employee.rank_id → rank.rank_id
- employee.designation_id → designation.designation_id
- crime_sub_head.crime_head_id → crime_head.crime_head_id
- section.act_id → act.act_id

### Important Notes
- Dates are stored as VARCHAR(20), format "YYYY-MM-DD" or "DD-MM-YYYY"
- Use LIKE for partial date matching: crime_registered_date LIKE '2024-07%'
- crime_no format: "Cr.No.XXX/YYYY"
- Join case_master with other tables using case_id FK
"""
