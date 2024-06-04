import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.models import NovaPoshta, post_novaposhta_association, Post, User
from src.services.exception_detail import ExDetail as Ex

API_KEY = settings.api_key_nova_poshta
API_URL = settings.api_url_nova_poshta


async def create_nova_poshta_warehouse(
    city: str, address_warehouse: str, category_warehouse: str, area: str, region: str, db: Session,
) -> NovaPoshta:
    db_warehouse = NovaPoshta(
        city=city,
        address_warehouse=address_warehouse,
        category_warehouse=category_warehouse,
        area=area,
        region=region,
    )

    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)

    return db_warehouse


async def get_all_warehouses(db: Session) -> list[NovaPoshta]:
    return db.query(NovaPoshta).all()


async def get_warehouses_data_for_specific_city(db: Session, city_name: str) -> list[str]:
    existing_warehouses = db.query(NovaPoshta).filter_by(city=city_name).all()
    existing_addresses = {warehouse.address_warehouse for warehouse in existing_warehouses}

    url = f"{API_URL}"
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "CityName": city_name
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, json=payload)

    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        print(f"Error: Request for city {city_name} was not successful.")
        return sorted(list(existing_addresses))

    warehouses_data = data.get("data", [])

    for item in warehouses_data:
        address_warehouse = item.get("Description", "")
        if address_warehouse not in existing_addresses:
            db_warehouse = await create_nova_poshta_warehouse(
                city=item.get("CityDescription", ""),
                address_warehouse=address_warehouse,
                category_warehouse=item.get("CategoryOfWarehouse", ""),
                area=item.get("SettlementAreaDescription", ""),
                region=item.get("SettlementRegionsDescription", ""),
                db=db
            )

            existing_addresses.add(db_warehouse.address_warehouse)

    all_warehouses = db.query(NovaPoshta).filter_by(city=city_name).order_by(NovaPoshta.id).all()

    return [warehouse.address_warehouse for warehouse in all_warehouses]


async def update_warehouses_data(db: Session) -> None:
    existing_cities = db.query(NovaPoshta.city).distinct().all()
    existing_cities = {city[0] for city in existing_cities}

    url = f"{API_URL}"
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "Limit": "",
            "Page": ""
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, json=payload)

    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        print("Error: Request was not successful.")
        return

    warehouses_data = data.get("data", [])

    for item in warehouses_data:
        city = item.get("CityDescription", "")
        if city in existing_cities:
            update_warehouse = db.query(NovaPoshta).filter_by(address_warehouse=item.get("Description", "")).first()

            if update_warehouse:
                update_warehouse.category_warehouse = item.get("CategoryOfWarehouse", "")
                update_warehouse.area = item.get("SettlementAreaDescription", "")
                update_warehouse.region = item.get("SettlementRegionsDescription", "")
            else:
                await create_nova_poshta_warehouse(
                    db=db,
                    city=city,
                    address_warehouse=item.get("Description", ""),
                    category_warehouse=item.get("CategoryOfWarehouse", ""),
                    area=item.get("SettlementAreaDescription", ""),
                    region=item.get("SettlementRegionsDescription", "")
                )
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
