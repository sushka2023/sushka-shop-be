import asyncio
from typing import Optional

import httpx
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.models import NovaPoshta, post_novaposhta_association, Post, User
from src.services.exception_detail import ExDetail as Ex
from src.services.nova_poshta import extract_warehouse_number, NUMBER_REGEX

logger = logging.getLogger(__name__)

API_KEY = settings.api_key_nova_poshta
API_URL = settings.api_url_nova_poshta


async def create_nova_poshta_warehouse(
    city: str,
    address_warehouse: str,
    category_warehouse: str,
    settle_ref: str,
    area: str,
    region: str,
    db: Session,
) -> NovaPoshta:
    db_warehouse = NovaPoshta(
        city=city,
        address_warehouse=address_warehouse,
        category_warehouse=category_warehouse,
        area=area,
        region=region,
        settlement_ref=settle_ref,
    )

    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)

    return db_warehouse


async def get_all_warehouses(db: Session) -> list[NovaPoshta]:
    return db.query(NovaPoshta).all()


async def get_warehouse_by_ref_and_address_warehouse(
    address_warehouse: str, settle_ref: str, db: Session
) -> NovaPoshta:
    warehouse = db.query(NovaPoshta).filter_by(
        settlement_ref=settle_ref, address_warehouse=address_warehouse, is_active=True
    ).first()

    return warehouse


async def get_warehouse_by_ref_and_number(
    settle_ref: str, category: str, db: Session, number: str = None,
) -> Optional[NovaPoshta]:
    query = db.query(NovaPoshta).filter(
        NovaPoshta.settlement_ref == settle_ref,
        NovaPoshta.category_warehouse == category,
        NovaPoshta.is_active == True,
    )
    if number:
        warehouses = query.all()
        for warehouse in warehouses:
            branch_number = extract_warehouse_number(warehouse.address_warehouse, NUMBER_REGEX)
            if branch_number == number:
                return warehouse
    else:
        return query.first()

    return None


async def get_warehouses_specific_city(settle_ref: str) -> list:
    url = f"{API_URL}"
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "SettlementRef": settle_ref
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, json=payload)

    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        logger.error(f"Error: Query for reference {settle_ref} was not successful.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to fetch warehouses from Nova Poshta")

    return data.get("data", [])


async def get_postomats(db: Session, settle_ref: str, search_term: str = None) -> list:
    if search_term:
        existing_postomat = await get_warehouse_by_ref_and_number(
            db=db, settle_ref=settle_ref, category="Поштомат", number=search_term
        )
        if existing_postomat:
            return [{"id": existing_postomat.id, "address_warehouse": existing_postomat.address_warehouse}]

    warehouse_data = await get_warehouses_specific_city(settle_ref=settle_ref)

    postomats = []
    for item in warehouse_data:
        address_warehouse = item.get("Description", "")
        city_name = item.get("SettlementDescription", "")
        area_name = item.get("SettlementAreaDescription", "")
        region_name = item.get("SettlementRegionsDescription", "")

        postomat_number = extract_warehouse_number(address=address_warehouse, regex=NUMBER_REGEX)

        if search_term and search_term not in postomat_number:
            continue

        if "поштомат" in address_warehouse.lower():
            existing_warehouse = await get_warehouse_by_ref_and_address_warehouse(
                settle_ref=settle_ref, address_warehouse=address_warehouse, db=db
            )

            if not existing_warehouse:
                new_warehouse = await create_nova_poshta_warehouse(
                    city=city_name,
                    area=area_name,
                    region=region_name,
                    address_warehouse=address_warehouse,
                    category_warehouse="Поштомат",
                    settle_ref=settle_ref,
                    db=db,
                )
                postomats.append({"id": new_warehouse.id, "address_warehouse": address_warehouse})
            else:
                postomats.append({"id": existing_warehouse.id, "address_warehouse": address_warehouse})

    return postomats


async def get_branches(db: Session, settle_ref: str, search_term: str = None) -> list:
    if search_term:
        existing_branch = await get_warehouse_by_ref_and_number(
            db=db, settle_ref=settle_ref, category="Відділення", number=search_term
        )
        if existing_branch:
            return [{"id": existing_branch.id, "address_warehouse": existing_branch.address_warehouse}]

    warehouse_data = await get_warehouses_specific_city(settle_ref=settle_ref)

    branches = []
    for item in warehouse_data:
        address_warehouse = item.get("Description", "")
        city_name = item.get("SettlementDescription", "")
        area_name = item.get("SettlementAreaDescription", "")
        region_name = item.get("SettlementRegionsDescription", "")

        branch_number = extract_warehouse_number(address=address_warehouse, regex=NUMBER_REGEX)

        if search_term and search_term not in branch_number:
            continue

        if "поштомат" not in address_warehouse.lower():
            existing_warehouse = await get_warehouse_by_ref_and_address_warehouse(
                settle_ref=settle_ref, address_warehouse=address_warehouse, db=db
            )

            if not existing_warehouse:
                new_warehouse = await create_nova_poshta_warehouse(
                    city=city_name,
                    area=area_name,
                    region=region_name,
                    address_warehouse=address_warehouse,
                    category_warehouse="Відділення",
                    settle_ref=settle_ref,
                    db=db,
                )
                branches.append({"id": new_warehouse.id, "address_warehouse": address_warehouse})
            else:
                branches.append({"id": existing_warehouse.id, "address_warehouse": address_warehouse})

    return branches


async def update_warehouses_data(db: Session) -> None:
    unique_refs = [
        ref[0] for ref in db.query(NovaPoshta.settlement_ref).distinct().all()
    ]

    for ref in unique_refs:
        warehouses_in_database = (
            db.query(NovaPoshta).filter_by(settlement_ref=ref).all()
        )

        url = f"{API_URL}"
        payload = {
            "apiKey": API_KEY,
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "SettlementRef": ref
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=payload)

        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            logger.error(f"Error: Query for reference {ref} was not successful.")
            continue

        warehouse_data = data.get("data", [])

        warehouses_from_api = []
        for item in warehouse_data:
            address_warehouse = item.get("Description", "")
            city_name = item.get("SettlementDescription", "")
            area_name = item.get("SettlementAreaDescription", "")
            region_name = item.get("SettlementRegionsDescription", "")
            if "поштомат" in address_warehouse.lower():
                category_warehouse = "Поштомат"
            else:
                category_warehouse = "Відділення"

            warehouses_from_api.append(
                {
                    "address_warehouse": address_warehouse,
                    "category_warehouse": category_warehouse,
                    "city": city_name,
                    "area": area_name,
                    "region": region_name,
                    "settlement_ref": ref
                }
            )

        warehouse_dict_db = {}
        for warehouse_db in warehouses_in_database:
            db_number = extract_warehouse_number(warehouse_db.address_warehouse, NUMBER_REGEX)
            if db_number:
                warehouse_dict_db[db_number] = warehouse_db

        api_numbers = set()
        for warehouse_api in warehouses_from_api:
            api_number = extract_warehouse_number(warehouse_api["address_warehouse"], NUMBER_REGEX)
            if not api_number:
                continue

            api_numbers.add(api_number)

            matched_warehouse_db = warehouse_dict_db.get(api_number)

            if matched_warehouse_db:
                # Update the address if it has changed
                if matched_warehouse_db.address_warehouse != warehouse_api["address_warehouse"]:
                    matched_warehouse_db.address_warehouse = warehouse_api["address_warehouse"]
                    logger.info(f"Updated address for warehouse: {matched_warehouse_db}")
                    db.add(matched_warehouse_db)
            else:
                # Add a new warehouse if not found in the database
                new_warehouse = await create_nova_poshta_warehouse(
                    city=warehouse_api["city"],
                    area=warehouse_api["area"],
                    region=warehouse_api["region"],
                    address_warehouse=warehouse_api["address_warehouse"],
                    category_warehouse=warehouse_api["category_warehouse"],
                    settle_ref=warehouse_api["settlement_ref"],
                    db=db,
                )
                logger.info(f"Added a new warehouse into database: {new_warehouse}")

        # Mark warehouses not found in the API response as inactive
        for warehouse_db in warehouses_in_database:
            db_number = extract_warehouse_number(warehouse_db.address_warehouse, NUMBER_REGEX)
            if db_number and db_number not in api_numbers:
                warehouse_db.is_active = False
                logger.info(f"Marked the warehouse as inactive: {warehouse_db}")

        await asyncio.sleep(2)

    db.commit()


async def delete_all_warehouses(db: Session) -> None:
    db.query(NovaPoshta).delete()
    db.commit()


async def get_nova_poshta_by_id(nova_poshta_id: int, db: Session) -> NovaPoshta | None:
    return db.query(NovaPoshta).filter_by(id=nova_poshta_id).first()


async def update_nova_poshta_data(
    db: Session, nova_poshta_id: int, nova_poshta_data: dict
) -> NovaPoshta:

    updated_data_nova_poshta = await get_nova_poshta_by_id(nova_poshta_id=nova_poshta_id, db=db)

    if not updated_data_nova_poshta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if updated_data_nova_poshta.address_warehouse:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)

    updated_data_nova_poshta.update_from_dict(nova_poshta_data)

    db.commit()
    db.refresh(updated_data_nova_poshta)

    return updated_data_nova_poshta


async def get_nova_poshta_warehouse(nova_poshta_id: int, user_id: int, db: Session):
    nova_poshta_warehouse = (
        db.query(NovaPoshta)
        .join(post_novaposhta_association)
        .join(Post)
        .join(User)
        .filter(
            NovaPoshta.is_delivery == False,
            NovaPoshta.id == nova_poshta_id,
            post_novaposhta_association.c.post_id == Post.id,
            Post.user_id == user_id
        )
        .first()
    )

    return nova_poshta_warehouse


async def get_nova_poshta_address_delivery(nova_poshta_id: int, user_id: int, db: Session):
    nova_poshta_address = (
        db.query(NovaPoshta)
        .join(post_novaposhta_association)
        .join(Post)
        .filter(
            NovaPoshta.is_delivery == True,
            NovaPoshta.id == nova_poshta_id,
            post_novaposhta_association.c.post_id == Post.id,
            Post.user_id == user_id
        )
        .first()
    )

    return nova_poshta_address
