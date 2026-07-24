"""Seed the database with realistic FIR data using Faker.

Usage:
    python -m app.db.seed          # from backend/
    python app/db/seed.py          # alternative
"""

import random
import sys
from pathlib import Path

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.models import (  # noqa: E402
    Act,
    ActSectionAssociation,
    Accused,
    ArrestSurrender,
    CaseCategory,
    CaseMaster,
    CaseStatusMaster,
    CasteMaster,
    ChargesheetDetails,
    ComplainantDetails,
    Court,
    CrimeHead,
    CrimeHeadActSection,
    CrimeSubHead,
    Designation,
    District,
    Employee,
    GravityOffence,
    OccupationMaster,
    Rank,
    ReligionMaster,
    Section,
    State,
    Unit,
    Victim,
)

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

KARNATAKA_DISTRICTS = [
    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Mangaluru",
    "Hubballi-Dharwad", "Belagavi", "Kalaburagi", "Ballari",
    "Vijayapura", "Bidar", "Raichur", "Koppal",
    "Gadag", "Haveri", "Davanagere", "Shivamogga",
    "Udupi", "Uttara Kannada", "Kodagu", "Hassan",
    "Tumakuru", "Chikkaballapura", "Kolar", "Ramanagara",
    "Chamarajanagar", "Yadgir", "Chitradurga", "Mandya",
]

CRIME_HEADS = [
    "Murder", "Rape", "Robbery", "Dacoity", "Kidnapping",
    "Theft", "Burglary", "Assault", "Cybercrime",
    "Drug Offences", "Fraud", "Domestic Violence",
    "Human Trafficking", "Arms Act", "Extortion",
]

CASE_CATEGORIES = ["Cognizable", "Non-Cognizable", "Compoundable"]
GRAVITY_LEVELS = ["Petty", "Serious", "Heinous"]
CASE_STATUSES = [
    "Registered", "Under Investigation", "Chargesheet Filed",
    "Convicted", "Acquitted", "Closed", "Pending Trial",
]
COURT_TYPES = ["Magistrate Court", "Sessions Court", "High Court", "Special Court"]
UNIT_TYPES = ["Police Station", "Sub-Division", "Circle", "District HQ"]
RANKS = [
    "Constable", "Head Constable", "ASI", "SI", "Inspector",
    "DSP", "ACP", "DCP", "Commissioner",
]
DESIGNATIONS = [
    "Patrol Officer", "Investigating Officer", "Station House Officer",
    "Sub-Inspector", "Deputy SP", "Additional SP",
]
CASTES = ["General", "SC", "ST", "OBC", "Category I", "Category II", "Category IIA"]
RELIGIONS = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain"]
OCCUPATIONS = [
    "Government Employee", "Private Employee", "Business", "Student",
    "Farmer", "Daily Wage Labourer", "Retired", "Unemployed",
    "Doctor", "Lawyer", "Teacher", "Engineer",
]

SECTIONS_DATA = [
    ("IPC", "302", "Murder"),
    ("IPC", "304", "Culpable Homicide"),
    ("IPC", "307", "Attempt to Murder"),
    ("IPC", "376", "Rape"),
    ("IPC", "379", "Theft"),
    ("IPC", "380", "Burglary"),
    ("IPC", "392", "Robbery"),
    ("IPC", "395", "Dacoity"),
    ("IPC", "420", "Cheating"),
    ("IPC", "498A", "Cruelty by Husband"),
    ("IPC", "506", "Criminal Intimidation"),
    ("IPC", "34", "Common Intention"),
    ("IPC", "147", "Rioting"),
    ("IPC", "148", "Rioting with Deadly Weapon"),
    ("IPC", "463", "Forgery"),
    ("IPC", "468", "Forgery for Cheating"),
    ("IPC", "471", "Using Forged Document"),
    ("BNS", "100", "Murder"),
    ("BNS", "115", "Voluntarily Causing Hurt"),
    ("BNS", "137", "Kidnapping"),
    ("BNS", "303", "Theft"),
    ("BNS", "316", "Criminal Breach of Trust"),
    ("BNS", "318", "Cheating"),
    ("BNS", "61", "Rape"),
    ("BNS", "111", "Extortion"),
    ("NDPS", "20", "Possession of Drugs"),
    ("NDPS", "29", "Drug Trafficking"),
    ("IT Act", "66", "Computer Related Offence"),
    ("IT Act", "66C", "Identity Theft"),
    ("IT Act", "66D", "Cheating by Impersonation"),
    ("Arms Act", "25", "Unlawful Possession of Arms"),
    ("Arms Act", "27", "Use of Illegal Arms"),
]

BENGALURU_COORDS = (12.9716, 77.5946)
KARNATAKA_COORDS = (15.3173, 75.7139)


def seed_reference_data(session: Session) -> dict:
    """Insert all reference/lookup tables. Returns dict of ID lists."""
    data = {}

    # States
    state = State(state_name="Karnataka")
    session.add(state)
    session.flush()
    data["state_id"] = state.state_id

    # Districts
    district_ids = []
    for name in KARNATAKA_DISTRICTS:
        d = District(district_name=name, state_id=state.state_id)
        session.add(d)
        session.flush()
        district_ids.append(d.district_id)
    data["district_ids"] = district_ids

    # Units (2 per district)
    unit_ids = []
    for did in district_ids:
        for i in range(2):
            u = Unit(
                unit_name=f"{fake.city()} PS-{i+1}",
                unit_type=random.choice(UNIT_TYPES),
                district_id=did,
            )
            session.add(u)
            session.flush()
            unit_ids.append(u.unit_id)
    data["unit_ids"] = unit_ids

    # Courts
    court_ids = []
    for ct in COURT_TYPES:
        c = Court(court_name=f"{fake.city()} {ct}", court_type=ct)
        session.add(c)
        session.flush()
        court_ids.append(c.court_id)
    data["court_ids"] = court_ids

    # Ranks
    rank_ids = []
    for r in RANKS:
        rk = Rank(rank_name=r)
        session.add(rk)
        session.flush()
        rank_ids.append(rk.rank_id)
    data["rank_ids"] = rank_ids

    # Designations
    desig_ids = []
    for d in DESIGNATIONS:
        dg = Designation(designation_name=d)
        session.add(dg)
        session.flush()
        desig_ids.append(dg.designation_id)
    data["desig_ids"] = desig_ids

    # Employees
    emp_ids = []
    for _ in range(50):
        e = Employee(
            name=fake.name(),
            badge_number=f"K{random.randint(10000, 99999)}",
            rank_id=random.choice(rank_ids),
            designation_id=random.choice(desig_ids),
            unit_id=random.choice(unit_ids),
        )
        session.add(e)
        session.flush()
        emp_ids.append(e.employee_id)
    data["emp_ids"] = emp_ids

    # Case categories
    cat_ids = []
    for name in CASE_CATEGORIES:
        cc = CaseCategory(category_name=name)
        session.add(cc)
        session.flush()
        cat_ids.append(cc.case_category_id)
    data["cat_ids"] = cat_ids

    # Gravity
    grav_ids = []
    for name in GRAVITY_LEVELS:
        g = GravityOffence(gravity_name=name)
        session.add(g)
        session.flush()
        grav_ids.append(g.gravity_offence_id)
    data["grav_ids"] = grav_ids

    # Case statuses
    status_ids = []
    for name in CASE_STATUSES:
        cs = CaseStatusMaster(status_name=name)
        session.add(cs)
        session.flush()
        status_ids.append(cs.case_status_id)
    data["status_ids"] = status_ids

    # Crime heads and sub heads
    head_ids = []
    for name in CRIME_HEADS:
        ch = CrimeHead(head_name=name)
        session.add(ch)
        session.flush()
        head_ids.append(ch.crime_head_id)
        # 1-3 sub heads per crime head
        for _ in range(random.randint(1, 3)):
            sh = CrimeSubHead(sub_head_name=f"{name} — {fake.word().title()}", crime_head_id=ch.crime_head_id)
            session.add(sh)
    data["head_ids"] = head_ids

    # Acts and sections
    act_map = {}
    section_map = {}
    for act_name, sec_num, desc in SECTIONS_DATA:
        if act_name not in act_map:
            a = Act(act_name=act_name)
            session.add(a)
            session.flush()
            act_map[act_name] = a.act_id
        s = Section(section_number=sec_num, description=desc, act_id=act_map[act_name])
        session.add(s)
        session.flush()
        section_map[(act_name, sec_num)] = (s.section_id, act_map[act_name])
    data["act_map"] = act_map
    data["section_map"] = section_map

    # Crime head <-> ActSection mappings
    for hid in random.sample(head_ids, min(10, len(head_ids))):
        for _ in range(random.randint(1, 3)):
            (act_name, sec_num) = random.choice(list(section_map.keys()))
            sid, aid = section_map[(act_name, sec_num)]
            chas = CrimeHeadActSection(crime_head_id=hid, act_id=aid, section_id=sid)
            session.add(chas)

    # Demographics
    caste_ids = []
    for name in CASTES:
        c = CasteMaster(caste_name=name)
        session.add(c)
        session.flush()
        caste_ids.append(c.caste_id)
    data["caste_ids"] = caste_ids

    religion_ids = []
    for name in RELIGIONS:
        r = ReligionMaster(religion_name=name)
        session.add(r)
        session.flush()
        religion_ids.append(r.religion_id)
    data["religion_ids"] = religion_ids

    occupation_ids = []
    for name in OCCUPATIONS:
        o = OccupationMaster(occupation_name=name)
        session.add(o)
        session.flush()
        occupation_ids.append(o.occupation_id)
    data["occupation_ids"] = occupation_ids

    return data


def seed_cases(session: Session, ref: dict, count: int = 120) -> None:
    """Generate `count` realistic FIR cases with related records."""
    for i in range(count):
        year = random.choice([2022, 2023, 2024, 2025])
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        reg_date = f"{year}-{month:02d}-{day:02d}"

        lat = KARNATAKA_COORDS[0] + random.uniform(-2, 2)
        lng = KARNATAKA_COORDS[1] + random.uniform(-2, 2)

        crime_no = f"0{year % 100}/{random.randint(10000, 99999)}"
        case_no = f"PS/{random.choice(['A','B','C','D'])}/{year}/{random.randint(100, 999)}"

        gravity = random.choice(ref["grav_ids"])
        if gravity == ref["grav_ids"][2]:  # Heinous
            status = random.choice(ref["status_ids"])
        else:
            status = random.choice(ref["status_ids"][:5])

        facts = fake.paragraph(nb_sentences=random.randint(3, 8))

        case = CaseMaster(
            case_no=case_no,
            crime_no=crime_no,
            crime_registered_date=reg_date,
            police_person_id=random.choice(ref["emp_ids"]),
            police_station_id=random.choice(ref["unit_ids"]),
            case_category_id=random.choice(ref["cat_ids"]),
            gravity_offence_id=gravity,
            crime_major_head_id=random.choice(ref["head_ids"]),
            case_status_id=status,
            court_id=random.choice(ref["court_ids"]),
            incident_from_date=f"{year}-{month:02d}-{max(1, day-5):02d}",
            incident_to_date=reg_date,
            latitude=round(lat, 6),
            longitude=round(lng, 6),
            brief_facts=facts,
        )
        session.add(case)
        session.flush()

        # Complainant
        comp = ComplainantDetails(
            case_id=case.case_id,
            name=fake.name(),
            age=random.randint(18, 75),
            gender=random.choice(["M", "F"]),
            address=fake.address(),
            phone=fake.phone_number()[:15],
        )
        session.add(comp)

        # 1-3 victims
        for _ in range(random.randint(1, 3)):
            v = Victim(
                case_id=case.case_id,
                name=fake.name(),
                age=random.randint(5, 80),
                gender=random.choice(["M", "F"]),
                address=fake.address(),
                caste_id=random.choice(ref["caste_ids"]),
                religion_id=random.choice(ref["religion_ids"]),
                occupation_id=random.choice(ref["occupation_ids"]),
            )
            session.add(v)

        # 1-4 accused
        num_accused = random.randint(1, 4)
        accused_names = []
        for _ in range(num_accused):
            aname = fake.name()
            accused_names.append(aname)
            a = Accused(
                case_id=case.case_id,
                name=aname,
                age=random.randint(18, 65),
                gender=random.choice(["M", "F"]),
                address=fake.address(),
                caste_id=random.choice(ref["caste_ids"]),
                religion_id=random.choice(ref["religion_ids"]),
                occupation_id=random.choice(ref["occupation_ids"]),
            )
            session.add(a)

        # Arrests (some cases)
        if random.random() < 0.6:
            for aname in random.sample(accused_names, k=min(len(accused_names), random.randint(1, num_accused))):
                ar = ArrestSurrender(
                    case_id=case.case_id,
                    accused_name=aname,
                    arrest_date=f"{year}-{month:02d}-{min(28, day+random.randint(1, 15)):02d}" if random.random() < 0.7 else None,
                    surrender_date=f"{year}-{month:02d}-{min(28, day+random.randint(1, 30)):02d}" if random.random() < 0.3 else None,
                    arrested_by=random.choice([ref["emp_ids"][i] for i in range(len(ref["emp_ids"]))]),
                )
                session.add(ar)

        # Act-section associations (1-3)
        for _ in range(random.randint(1, 3)):
            (act_name, sec_num) = random.choice(list(ref["section_map"].keys()))
            sid, aid = ref["section_map"][(act_name, sec_num)]
            asa = ActSectionAssociation(
                case_id=case.case_id,
                act_id=aid,
                section_id=sid,
            )
            session.add(asa)

        # Chargesheet (for some)
        if random.random() < 0.4:
            cs = ChargesheetDetails(
                case_id=case.case_id,
                chargesheet_date=f"{year}-{min(12, month+random.randint(1, 6)):02d}-{random.randint(1, 28):02d}",
                investigating_officer=random.choice([ref["emp_ids"][i] for i in range(len(ref["emp_ids"]))]),
                chargesheet_number=f"CS/{year}/{random.randint(1000, 9999)}",
            )
            session.add(cs)

    session.commit()
    print(f"✓ Seeded {count} cases with related records")


def main() -> None:
    from app.config import settings

    engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"))

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.execute(text("SELECT COUNT(*) FROM case_master")).scalar()
        if existing and existing > 0:
            print(f"Database already has {existing} cases. Skipping seed.")
            return

        print("Seeding reference data...")
        ref = seed_reference_data(session)
        print(f"✓ Reference data: {len(ref['district_ids'])} districts, {len(ref['unit_ids'])} units, {len(ref['emp_ids'])} employees")

        print("Seeding cases...")
        seed_cases(session, ref, count=120)


if __name__ == "__main__":
    main()
