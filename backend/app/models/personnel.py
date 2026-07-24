from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.case import CaseMaster
    from app.models.geography import Unit


class Rank(Base):
    __tablename__ = "rank"

    rank_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    rank_name: Mapped[str] = mapped_column(String(100), nullable=False)

    employees: Mapped[list[Employee]] = relationship(
        back_populates="rank"
    )


class Designation(Base):
    __tablename__ = "designation"

    designation_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    designation_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    employees: Mapped[list[Employee]] = relationship(
        back_populates="designation"
    )


class Employee(Base):
    __tablename__ = "employee"

    employee_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    badge_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    rank_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    designation_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    unit_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    rank: Mapped[Rank | None] = relationship(
        back_populates="employees"
    )
    designation: Mapped[Designation | None] = relationship(
        back_populates="employees"
    )
    unit: Mapped[Unit | None] = relationship(
        back_populates="employees"
    )
    cases: Mapped[list[CaseMaster]] = relationship(
        back_populates="officer"
    )
