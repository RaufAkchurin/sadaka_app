import asyncio
import json
import os

from sqlalchemy import insert

from app.dao.database import Base, async_session_maker, engine
from app.documents.models import Document
from app.fund.models import Fund
from app.geo.models import City, Country, Region
from app.payments.models import Payment
from app.project.models import Project, Stage
from app.users.models import Role, User


def open_mock_json(model: str):
    test_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(test_dir, f"../tests/mocks/mock_{model}.json")
    with open(file_path, "r") as file:
        return json.load(file)


async def prepare_database_core(session):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        country = open_mock_json("country")
        region = open_mock_json("region")
        city = open_mock_json("city")

        users = open_mock_json("user")
        roles = open_mock_json("role")

        funds = open_mock_json("fund")
        projects = open_mock_json("project")
        stages = open_mock_json("stage")

        documents = open_mock_json("document")
        payments = open_mock_json("payment")

        async with async_session_maker() as session:
            add_country = insert(Country).values(country)
            add_region = insert(Region).values(region)
            add_city = insert(City).values(city)

            add_users = insert(User).values(users)
            add_roles = insert(Role).values(roles)

            add_funds = insert(Fund).values(funds)
            add_projects = insert(Project).values(projects)
            add_stages = insert(Stage).values(stages)

            add_documents = insert(Document).values(documents)
            add_payments = insert(Payment).values(payments)

            await session.execute(add_country)
            await session.execute(add_region)
            await session.execute(add_city)

            await session.execute(add_users)
            await session.execute(add_roles)

            await session.execute(add_funds)
            await session.execute(add_projects)
            await session.execute(add_stages)

            await session.execute(add_documents)
            await session.execute(add_payments)

            await session.commit()
    except:  # noqa E722
        await session.rollback()
        raise
    finally:
        await session.close()


if __name__ == "__main__":

    async def main():
        async with async_session_maker() as session:
            await prepare_database_core(session)

    asyncio.run(main())
