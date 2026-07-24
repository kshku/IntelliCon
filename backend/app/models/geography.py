from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.case import CaseMaster
    from app.models.personnel import Employee


class State(Base):
    __tablename__ = "state"

    state_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state_name: Mapped[str] = mapped_column(String(100), nullable=False)

    districts: Mapped[list[District]] = relationship(back_populates="state")


class District(Base):
    __tablename__ = "district"

    district_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_id: Mapped[int] = mapped_column(Integer, nullable=False)

    state: Mapped[State] = relationship(back_populates="districts")
    units: Mapped[list[Unit]] = relationship(back_populates="district")


class Unit(Base):
    __tablename__ = "unit"

    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unit_name: Mapped[str] = mapped_column(String(150), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    district_id: Mapped[int] = mapped_column(Integer, nullable=False)

    district: Mapped[District] = relationship(back_populates="units")
    employees: Mapped[list[Employee]] = relationship(back_populates="unit")


class Court(Base):
    __tablename__ = "court"

    court_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    court_name: Mapped[str] = mapped_column(String(200), nullable=False)
    court_type: Mapped[str] = mapped_column(String(50), nullable=False)

    cases: Mapped[list[CaseMaster]] = relationship(back_populates="court")
