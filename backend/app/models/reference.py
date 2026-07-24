from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CaseCategory(Base):
    __tablename__ = "case_category"

    case_category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(150), nullable=False)

    cases: Mapped[list["CaseMaster"]] = relationship(back_populates="category")


class GravityOffence(Base):
    __tablename__ = "gravity_offence"

    gravity_offence_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gravity_name: Mapped[str] = mapped_column(String(100), nullable=False)

    cases: Mapped[list["CaseMaster"]] = relationship(back_populates="gravity")


class CaseStatusMaster(Base):
    __tablename__ = "case_status_master"

    case_status_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status_name: Mapped[str] = mapped_column(String(100), nullable=False)

    cases: Mapped[list["CaseMaster"]] = relationship(back_populates="status")


class CrimeHead(Base):
    __tablename__ = "crime_head"

    crime_head_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    head_name: Mapped[str] = mapped_column(String(200), nullable=False)

    sub_heads: Mapped[list["CrimeSubHead"]] = relationship(back_populates="crime_head")
    act_sections: Mapped[list["CrimeHeadActSection"]] = relationship(back_populates="crime_head")


class CrimeSubHead(Base):
    __tablename__ = "crime_sub_head"

    crime_sub_head_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sub_head_name: Mapped[str] = mapped_column(String(200), nullable=False)
    crime_head_id: Mapped[int] = mapped_column(Integer, nullable=False)

    crime_head: Mapped["CrimeHead"] = relationship(back_populates="sub_heads")


class Act(Base):
    __tablename__ = "act"

    act_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    act_name: Mapped[str] = mapped_column(Text, nullable=False)

    sections: Mapped[list["Section"]] = relationship(back_populates="act")
    crime_head_sections: Mapped[list["CrimeHeadActSection"]] = relationship(back_populates="act")


class Section(Base):
    __tablename__ = "section"

    section_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_number: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    act_id: Mapped[int] = mapped_column(Integer, nullable=False)

    act: Mapped["Act"] = relationship(back_populates="sections")


class CrimeHeadActSection(Base):
    __tablename__ = "crime_head_act_section"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crime_head_id: Mapped[int] = mapped_column(Integer, nullable=False)
    act_id: Mapped[int] = mapped_column(Integer, nullable=False)
    section_id: Mapped[int] = mapped_column(Integer, nullable=False)

    crime_head: Mapped["CrimeHead"] = relationship(back_populates="act_sections")
    act: Mapped["Act"] = relationship(back_populates="crime_head_sections")


class CasteMaster(Base):
    __tablename__ = "caste_master"

    caste_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caste_name: Mapped[str] = mapped_column(String(100), nullable=False)


class ReligionMaster(Base):
    __tablename__ = "religion_master"

    religion_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    religion_name: Mapped[str] = mapped_column(String(100), nullable=False)


class OccupationMaster(Base):
    __tablename__ = "occupation_master"

    occupation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    occupation_name: Mapped[str] = mapped_column(String(100), nullable=False)
