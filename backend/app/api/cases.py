from __future__ import annotations

import csv
import io
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.sync import sync_all
from app.models import (
    Accused,
    CaseMaster,
    CaseStatusMaster,
    ComplainantDetails,
    CrimeHead,
    Unit,
    Victim,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["cases"])


class SearchResult(BaseModel):
    case_id: int
    case_no: str
    crime_no: str | None = None
    brief_facts: str | None = None
    crime_registered_date: str | None = None


class PersonOut(BaseModel):
    name: str
    age: int | None = None
    gender: str | None = None


class CaseDetailsOut(BaseModel):
    case_id: int
    case_no: str
    crime_no: str | None = None
    crime_registered_date: str | None = None
    incident_from_date: str | None = None
    incident_to_date: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    brief_facts: str | None = None
    station_name: str
    status_name: str
    crime_type: str
    complainants: list[PersonOut]
    accused: list[PersonOut]
    victims: list[PersonOut]


class UploadPayload(BaseModel):
    file_content: str
    filename: str


@router.get("/search", response_model=list[SearchResult])
async def search_cases(q: str = "", session: AsyncSession = Depends(get_session)):
    if not q:
        query = select(CaseMaster).order_by(desc(CaseMaster.case_id)).limit(10)
    else:
        search_filter = or_(
            CaseMaster.case_no.ilike(f"%{q}%"),
            CaseMaster.crime_no.ilike(f"%{q}%"),
            CaseMaster.brief_facts.ilike(f"%{q}%"),
        )
        query = select(CaseMaster).where(search_filter).limit(20)

    result = await session.execute(query)
    cases = result.scalars().all()

    return [
        SearchResult(
            case_id=c.case_id,
            case_no=c.case_no,
            crime_no=c.crime_no,
            brief_facts=(c.brief_facts[:200] + "...") if c.brief_facts else None,
            crime_registered_date=c.crime_registered_date,
        )
        for c in cases
    ]


@router.get("/{case_id}", response_model=CaseDetailsOut)
async def get_case_details(case_id: int, session: AsyncSession = Depends(get_session)):
    query = select(CaseMaster).where(CaseMaster.case_id == case_id)
    result = await session.execute(query)
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")

    res_compl = await session.execute(
        select(ComplainantDetails).where(ComplainantDetails.case_id == case_id)
    )
    complainants = res_compl.scalars().all()

    res_accused = await session.execute(select(Accused).where(Accused.case_id == case_id))
    accused = res_accused.scalars().all()

    res_victim = await session.execute(select(Victim).where(Victim.case_id == case_id))
    victims = res_victim.scalars().all()

    station_name = "Unknown PS"
    if c.police_station_id:
        res_unit = await session.execute(select(Unit).where(Unit.unit_id == c.police_station_id))
        unit = res_unit.scalar_one_or_none()
        if unit:
            station_name = unit.unit_name

    status_name = "Registered"
    if c.case_status_id:
        res_status = await session.execute(
            select(CaseStatusMaster).where(CaseStatusMaster.case_status_id == c.case_status_id)
        )
        status_obj = res_status.scalar_one_or_none()
        if status_obj:
            status_name = status_obj.status_name

    crime_type = "IPC Offence"
    if c.crime_major_head_id:
        res_head = await session.execute(
            select(CrimeHead).where(CrimeHead.crime_head_id == c.crime_major_head_id)
        )
        head = res_head.scalar_one_or_none()
        if head:
            crime_type = head.head_name

    return CaseDetailsOut(
        case_id=c.case_id,
        case_no=c.case_no,
        crime_no=c.crime_no,
        crime_registered_date=c.crime_registered_date,
        incident_from_date=c.incident_from_date,
        incident_to_date=c.incident_to_date,
        latitude=c.latitude,
        longitude=c.longitude,
        brief_facts=c.brief_facts,
        station_name=station_name,
        status_name=status_name,
        crime_type=crime_type,
        complainants=[PersonOut(name=p.name, age=p.age, gender=p.gender) for p in complainants],
        accused=[PersonOut(name=p.name, age=p.age, gender=p.gender) for p in accused],
        victims=[PersonOut(name=p.name, age=p.age, gender=p.gender) for p in victims],
    )


@router.post("/upload")
async def upload_cases(payload: UploadPayload, session: AsyncSession = Depends(get_session)):
    filename = payload.filename.lower()
    content = payload.file_content
    records = []

    if filename.endswith(".json"):
        try:
            records = json.loads(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    elif filename.endswith(".csv"):
        try:
            reader = csv.DictReader(io.StringIO(content))
            records = list(reader)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Only CSV or JSON files are supported")

    inserted_count = 0
    for r in records:
        case_no = r.get("case_no")
        if not case_no:
            continue

        existing = await session.execute(select(CaseMaster).where(CaseMaster.case_no == case_no))
        if existing.scalar_one_or_none():
            continue

        ps_name = r.get("police_station", "Koramangala PS")
        res_unit = await session.execute(select(Unit).where(Unit.unit_name == ps_name))
        unit = res_unit.scalar_one_or_none()
        if not unit:
            unit = Unit(unit_name=ps_name, unit_type="Police Station")
            session.add(unit)
            await session.flush()

        status_name = r.get("status", "Under Investigation")
        res_status = await session.execute(
            select(CaseStatusMaster).where(CaseStatusMaster.status_name == status_name)
        )
        status_obj = res_status.scalar_one_or_none()
        if not status_obj:
            status_obj = CaseStatusMaster(status_name=status_name)
            session.add(status_obj)
            await session.flush()

        ch_name = r.get("crime_head", "Theft")
        res_head = await session.execute(select(CrimeHead).where(CrimeHead.head_name == ch_name))
        head = res_head.scalar_one_or_none()
        if not head:
            head = CrimeHead(head_name=ch_name)
            session.add(head)
            await session.flush()

        lat = None
        lon = None
        try:
            if r.get("latitude"):
                lat = float(r.get("latitude"))
            if r.get("longitude"):
                lon = float(r.get("longitude"))
        except ValueError:
            pass

        case = CaseMaster(
            case_no=case_no,
            crime_no=r.get("crime_no"),
            crime_registered_date=r.get("crime_registered_date", "2026-07-26"),
            police_station_id=unit.unit_id,
            case_status_id=status_obj.case_status_id,
            crime_major_head_id=head.crime_head_id,
            latitude=lat,
            longitude=lon,
            brief_facts=r.get("brief_facts", "No description provided."),
        )
        session.add(case)
        await session.flush()

        comp_name = r.get("complainant_name")
        if comp_name:
            comp = ComplainantDetails(case_id=case.case_id, name=comp_name)
            session.add(comp)

        acc_name = r.get("accused_name")
        if acc_name:
            acc = Accused(case_id=case.case_id, name=acc_name)
            session.add(acc)

        inserted_count += 1

    await session.commit()

    try:
        await sync_all()
    except Exception as exc:
        logger.warning("Failed to sync uploaded data to Neo4j: %s", exc)

    return {"message": "Data uploaded successfully", "inserted_count": inserted_count}
