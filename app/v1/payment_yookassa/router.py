from fastapi import APIRouter, Depends, Path, Query, Response
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.models.user import User
from app.v1.dependencies.auth_dep import get_current_user
from app.v1.dependencies.dao_dep import get_session_with_commit
from app.v1.payment_yookassa.schemas import YooPaymentUrlSchema
from app.v1.payment_yookassa.use_cases.callback import YooCallbackSuccessUseCaseImpl
from app.v1.payment_yookassa.use_cases.create_payment import CreateYooPaymentUseCaseImpl

v1_yookassa_router = APIRouter()


@v1_yookassa_router.post("/{project_id}/{amount}", response_model=YooPaymentUrlSchema)
async def yookassa_create_payment(
    session: AsyncSession = Depends(get_session_with_commit),
    project_id: int = Path(gt=0, description="ID проекта"),
    amount: int = Path(gt=0, description="Сумма платежа"),
    user_data: User = Depends(get_current_user),
    return_url: Url = Query(default="http://sadaka_app_domain/app/v1/thaks_page", alias="return_url"),
) -> YooPaymentUrlSchema:
    use_case = CreateYooPaymentUseCaseImpl(
        session=session,
        amount=amount,
        user_data=user_data,
        project_id=project_id,
        return_url=return_url,
    )
    redirect_url = await use_case.execute()
    return redirect_url


@v1_yookassa_router.post("/callback")
async def yookassa_success_callback(
    request: Request,
    session: AsyncSession = Depends(get_session_with_commit),
) -> Response:
    use_case = YooCallbackSuccessUseCaseImpl(request=request, session=session)
    await use_case.execute()

    return Response(status_code=200)
