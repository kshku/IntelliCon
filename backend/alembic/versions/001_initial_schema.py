"""initial schema — 25 tables

Revision ID: 001_initial
Revises:
Create Date: 2025-07-25
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Geography
    op.create_table(
        "state",
        sa.Column(
            "state_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "state_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "district",
        sa.Column(
            "district_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "district_name", sa.String(100), nullable=False,
        ),
        sa.Column("state_id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "unit",
        sa.Column(
            "unit_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "unit_name", sa.String(150), nullable=False,
        ),
        sa.Column(
            "unit_type", sa.String(50), nullable=False,
        ),
        sa.Column("district_id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "court",
        sa.Column(
            "court_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "court_name", sa.String(200), nullable=False,
        ),
        sa.Column(
            "court_type", sa.String(50), nullable=False,
        ),
    )

    # Personnel
    op.create_table(
        "rank",
        sa.Column(
            "rank_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "rank_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "designation",
        sa.Column(
            "designation_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "designation_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "employee",
        sa.Column(
            "employee_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "name", sa.String(150), nullable=False,
        ),
        sa.Column(
            "badge_number", sa.String(50), nullable=True,
        ),
        sa.Column("rank_id", sa.Integer(), nullable=True),
        sa.Column("designation_id", sa.Integer(), nullable=True),
        sa.Column("unit_id", sa.Integer(), nullable=True),
    )

    # Reference
    op.create_table(
        "case_category",
        sa.Column(
            "case_category_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "category_name", sa.String(150), nullable=False,
        ),
    )
    op.create_table(
        "gravity_offence",
        sa.Column(
            "gravity_offence_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "gravity_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "case_status_master",
        sa.Column(
            "case_status_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "status_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "crime_head",
        sa.Column(
            "crime_head_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "head_name", sa.String(200), nullable=False,
        ),
    )
    op.create_table(
        "crime_sub_head",
        sa.Column(
            "crime_sub_head_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "sub_head_name", sa.String(200), nullable=False,
        ),
        sa.Column("crime_head_id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "act",
        sa.Column(
            "act_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column("act_name", sa.Text(), nullable=False),
    )
    op.create_table(
        "section",
        sa.Column(
            "section_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "section_number", sa.String(50), nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("act_id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "crime_head_act_section",
        sa.Column(
            "id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column("crime_head_id", sa.Integer(), nullable=False),
        sa.Column("act_id", sa.Integer(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "caste_master",
        sa.Column(
            "caste_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "caste_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "religion_master",
        sa.Column(
            "religion_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "religion_name", sa.String(100), nullable=False,
        ),
    )
    op.create_table(
        "occupation_master",
        sa.Column(
            "occupation_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "occupation_name", sa.String(100), nullable=False,
        ),
    )

    # Case
    op.create_table(
        "case_master",
        sa.Column(
            "case_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_no", sa.String(50),
            nullable=False, unique=True,
        ),
        sa.Column(
            "crime_no", sa.String(50),
            nullable=True, unique=True,
        ),
        sa.Column(
            "crime_registered_date",
            sa.String(20),
            nullable=True,
        ),
        sa.Column(
            "police_person_id", sa.Integer(),
            sa.ForeignKey("employee.employee_id"),
            nullable=True,
        ),
        sa.Column(
            "police_station_id", sa.Integer(),
            sa.ForeignKey("unit.unit_id"),
            nullable=True,
        ),
        sa.Column(
            "case_category_id", sa.Integer(),
            sa.ForeignKey(
                "case_category.case_category_id"
            ),
            nullable=True,
        ),
        sa.Column(
            "gravity_offence_id", sa.Integer(),
            sa.ForeignKey(
                "gravity_offence.gravity_offence_id"
            ),
            nullable=True,
        ),
        sa.Column(
            "crime_major_head_id", sa.Integer(),
            sa.ForeignKey("crime_head.crime_head_id"),
            nullable=True,
        ),
        sa.Column(
            "crime_minor_head_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "case_status_id", sa.Integer(),
            sa.ForeignKey(
                "case_status_master.case_status_id"
            ),
            nullable=True,
        ),
        sa.Column(
            "court_id", sa.Integer(),
            sa.ForeignKey("court.court_id"),
            nullable=True,
        ),
        sa.Column(
            "incident_from_date",
            sa.String(20),
            nullable=True,
        ),
        sa.Column(
            "incident_to_date",
            sa.String(20),
            nullable=True,
        ),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("brief_facts", sa.Text(), nullable=True),
    )
    op.create_table(
        "complainant_details",
        sa.Column(
            "complainant_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_id", sa.Integer(),
            sa.ForeignKey("case_master.case_id"),
            nullable=False,
        ),
        sa.Column(
            "name", sa.String(150), nullable=False,
        ),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column(
            "gender", sa.String(10), nullable=True,
        ),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column(
            "phone", sa.String(20), nullable=True,
        ),
    )
    op.create_table(
        "victim",
        sa.Column(
            "victim_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_id", sa.Integer(),
            sa.ForeignKey("case_master.case_id"),
            nullable=False,
        ),
        sa.Column(
            "name", sa.String(150), nullable=False,
        ),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column(
            "gender", sa.String(10), nullable=True,
        ),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("caste_id", sa.Integer(), nullable=True),
        sa.Column(
            "religion_id", sa.Integer(), nullable=True,
        ),
        sa.Column(
            "occupation_id", sa.Integer(), nullable=True,
        ),
    )
    op.create_table(
        "accused",
        sa.Column(
            "accused_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_id", sa.Integer(),
            sa.ForeignKey("case_master.case_id"),
            nullable=False,
        ),
        sa.Column(
            "name", sa.String(150), nullable=False,
        ),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column(
            "gender", sa.String(10), nullable=True,
        ),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("caste_id", sa.Integer(), nullable=True),
        sa.Column(
            "religion_id", sa.Integer(), nullable=True,
        ),
        sa.Column(
            "occupation_id", sa.Integer(), nullable=True,
        ),
    )
    op.create_table(
        "arrest_surrender",
        sa.Column(
            "arrest_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_id", sa.Integer(),
            sa.ForeignKey("case_master.case_id"),
            nullable=False,
        ),
        sa.Column(
            "accused_name", sa.String(150), nullable=False,
        ),
        sa.Column(
            "arrest_date", sa.String(20), nullable=True,
        ),
        sa.Column(
            "surrender_date", sa.String(20), nullable=True,
        ),
        sa.Column(
            "arrested_by", sa.String(150), nullable=True,
        ),
    )
    op.create_table(
        "act_section_association",
        sa.Column(
            "id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_id", sa.Integer(),
            sa.ForeignKey("case_master.case_id"),
            nullable=False,
        ),
        sa.Column("act_id", sa.Integer(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
    )
    op.create_table(
        "chargesheet_details",
        sa.Column(
            "chargesheet_id", sa.Integer(),
            primary_key=True, autoincrement=True,
        ),
        sa.Column(
            "case_id", sa.Integer(),
            sa.ForeignKey("case_master.case_id"),
            nullable=False,
        ),
        sa.Column(
            "chargesheet_date",
            sa.String(20),
            nullable=True,
        ),
        sa.Column(
            "investigating_officer",
            sa.String(150),
            nullable=True,
        ),
        sa.Column(
            "chargesheet_number",
            sa.String(50),
            nullable=True,
        ),
    )

    # Performance indexes
    op.create_index(
        "ix_case_master_case_no",
        "case_master", ["case_no"],
    )
    op.create_index(
        "ix_case_master_crime_no",
        "case_master", ["crime_no"],
    )
    op.create_index(
        "ix_case_master_crime_registered_date",
        "case_master", ["crime_registered_date"],
    )
    op.create_index(
        "ix_case_master_case_status_id",
        "case_master", ["case_status_id"],
    )
    op.create_index(
        "ix_case_master_case_category_id",
        "case_master", ["case_category_id"],
    )
    op.create_index(
        "ix_case_master_police_station_id",
        "case_master", ["police_station_id"],
    )
    op.create_index(
        "ix_case_master_crime_major_head_id",
        "case_master", ["crime_major_head_id"],
    )
    op.create_index(
        "ix_case_master_court_id",
        "case_master", ["court_id"],
    )
    op.create_index(
        "ix_case_master_location",
        "case_master", ["latitude", "longitude"],
    )
    op.create_index(
        "ix_complainant_details_case_id",
        "complainant_details", ["case_id"],
    )
    op.create_index(
        "ix_victim_case_id", "victim", ["case_id"],
    )
    op.create_index(
        "ix_accused_case_id", "accused", ["case_id"],
    )
    op.create_index(
        "ix_arrest_surrender_case_id",
        "arrest_surrender", ["case_id"],
    )
    op.create_index(
        "ix_act_section_association_case_id",
        "act_section_association", ["case_id"],
    )
    op.create_index(
        "ix_chargesheet_details_case_id",
        "chargesheet_details", ["case_id"],
    )
    op.create_index(
        "ix_employee_unit_id",
        "employee", ["unit_id"],
    )


def downgrade() -> None:
    op.drop_table("chargesheet_details")
    op.drop_table("act_section_association")
    op.drop_table("arrest_surrender")
    op.drop_table("accused")
    op.drop_table("victim")
    op.drop_table("complainant_details")
    op.drop_table("case_master")
    op.drop_table("occupation_master")
    op.drop_table("religion_master")
    op.drop_table("caste_master")
    op.drop_table("crime_head_act_section")
    op.drop_table("section")
    op.drop_table("act")
    op.drop_table("crime_sub_head")
    op.drop_table("crime_head")
    op.drop_table("case_status_master")
    op.drop_table("gravity_offence")
    op.drop_table("case_category")
    op.drop_table("employee")
    op.drop_table("designation")
    op.drop_table("rank")
    op.drop_table("court")
    op.drop_table("unit")
    op.drop_table("district")
    op.drop_table("state")
