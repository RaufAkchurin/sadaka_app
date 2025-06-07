from typing import Any

from admin.views.base.picture_preview import AdminPicturePreview
from fastapi import UploadFile
from models.geo import Region
from starlette.requests import Request
from v1.dependencies.dao_dep import get_session_with_commit
from v1.dependencies.s3 import get_s3_client
from v1.geo.use_cases.region.update_picture import RegionPictureUpdateUseCaseImpl
from v1.s3_storage.use_cases.s3_upload import S3UploadUseCaseImpl
from v1.users.dao import RegionDAO
from wtforms import FileField


class PictureUploadRelated(AdminPicturePreview):
    def __init__(self):
        super().__init__()
        self.s3_client = get_s3_client()

    async def scaffold_form(self, form_rules=None):
        form_class = await super().scaffold_form()
        form_class.upload = FileField()  # we always have it, but without file it size == 0
        return form_class

    # async def insert_model(self, request: Request, data: dict):
    #     file: UploadFile = data.pop("upload")
    #
    #     if file and file.filename:
    #         use_case = S3UploadUseCaseImpl(s3_client=self.s3_client)
    #         s3_file = await use_case(file=file)
    #         data["url"] = s3_file.url
    #
    #     return await super().insert_model(request, data)

    # async def update_model(self, request, pk, data):
    #     file: UploadFile = data.pop("upload")
    #
    #     async for session in  get_session_with_commit():
    #         region_dao = RegionDAO(session=session)
    #         region = await region_dao.find_one_or_none_by_id(data_id=int(pk))
    #
    #
    #         if file.size != 0:
    #             use_case = RegionPictureUpdateUseCaseImpl(session=session, s3_client=self.s3_client)
    #             uploaded_picture_url = await use_case(region=region, picture=file)
    #             data["url"] = uploaded_picture_url.url
    #
    #         await session.aclose()
    #     return await super().update_model(request, pk, data)

    # async def after_model_change(
    #     self, data: dict, model: Any, is_created: bool, request: Request
    # ) -> None:
    #     """Perform some actions after a model was created
    #     or updated and committed to the database.
    #     By default does nothing.
    #     """
    #
    #     file: UploadFile = data.pop("upload")
    #
    #     async for session in  get_session_with_commit():
    #         region_dao = RegionDAO(session=session)
    #         region = await region_dao.find_one_or_none_by_id(data_id=int(pk))
    #
    #
    #         if file.size != 0:
    #             use_case = RegionPictureUpdateUseCaseImpl(session=session, s3_client=self.s3_client)
    #             uploaded_picture_url = await use_case(region=region, picture=file)
    #             data["url"] = uploaded_picture_url.url
    #
    #         await session.aclose()


class RegionAdmin(PictureUploadRelated, model=Region):
    icon = "fa-solid fa-map"
    name = "Регион"
    name_plural = "Регионы"

    column_list = ["name", "picture_url"]
    form_columns = [Region.name, Region.country, Region.citys, Region.funds]
