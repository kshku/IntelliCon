from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.geography import Court, Unit
    from app.models.personnel import Employee
    from app.models.reference import (
        CaseCategory,
        CaseStatusMaster,
        CrimeHead,
        GravityOffence,
    )


class CaseMaster(Base):
    __tablename__ = "case_master"

    case_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_no: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    crime_no: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    crime_registered_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    police_person_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("employee.employee_id"),
        nullable=True,
    )
    police_station_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("unit.unit_id"),
        nullable=True,
    )
    case_category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("case_category.case_category_id"),
        nullable=True,
    )
    gravity_offence_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("gravity_offence.gravity_offence_id"),
        nullable=True,
    )
    crime_major_head_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("crime_head.crime_head_id"),
        nullable=True,
    )
    crime_minor_head_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    case_status_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("case_status_master.case_status_id"),
        nullable=True,
    )
    court_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("court.court_id"),
        nullable=True,
    )
    incident_from_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    incident_to_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    brief_facts: Mapped[str | None] = mapped_column(Text, nullable=True)

    officer: Mapped[Employee | None] = relationship(
        back_populates="cases",
        foreign_keys=[police_person_id],
    )
    police_station: Mapped[Unit | None] = relationship(foreign_keys=[police_station_id])
    category: Mapped[CaseCategory | None] = relationship(back_populates="cases")
    gravity: Mapped[GravityOffence | None] = relationship(back_populates="cases")
    crime_head: Mapped[CrimeHead | None] = relationship(foreign_keys=[crime_major_head_id])
    status: Mapped[CaseStatusMaster | None] = relationship(back_populates="cases")
    court: Mapped[Court | None] = relationship(back_populates="cases")

    complainants: Mapped[list[ComplainantDetails]] = relationship(back_populates="case")
    victims: Mapped[list[Victim]] = relationship(back_populates="case")
    accused: Mapped[list[Accused]] = relationship(back_populates="case")
    arrests: Mapped[list[ArrestSurrender]] = relationship(back_populates="case")
    act_sections: Mapped[list[ActSectionAssociation]] = relationship(back_populates="case")
    chargesheets: Mapped[list[ChargesheetDetails]] = relationship(back_populates="case")


class ComplainantDetails(Base):
    __tablename__ = "complainant_details"

    complainant_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("case_master.case_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="complainants")


class Victim(Base):
    __tablename__ = "victim"

    victim_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("case_master.case_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    caste_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    religion_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="victims")


class Accused(Base):
    __tablename__ = "accused"

    accused_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("case_master.case_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    caste_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    religion_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="accused")


class ArrestSurrender(Base):
    __tablename__ = "arrest_surrender"

    arrest_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("case_master.case_id"),
        nullable=False,
    )
    accused_name: Mapped[str] = mapped_column(String(150), nullable=False)
    arrest_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    surrender_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    arrested_by: Mapped[str | None] = mapped_column(String(150), nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="arrests")


class ActSectionAssociation(Base):
    __tablename__ = "act_section_association"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("case_master.case_id"),
        nullable=False,
    )
    act_id: Mapped[int] = mapped_column(Integer, nullable=False)
    section_id: Mapped[int] = mapped_column(Integer, nullable=False)

    case: Mapped[CaseMaster] = relationship(back_populates="act_sections")


class ChargesheetDetails(Base):
    __tablename__ = "chargesheet_details"

    chargesheet_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("case_master.case_id"),
        nullable=False,
    )
    chargesheet_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    investigating_officer: Mapped[str | None] = mapped_column(String(150), nullable=True)
    chargesheet_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="chargesheets")
