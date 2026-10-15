import uuid
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.core.exceptions import DatabaseException
from src.models.user import UserRole, User
from src.utils.dependencies import RoleChecker, get_current_user
from src.schemas.order import OrderResponseSchema, OrderCreateSchema
from src.services.order_services import OrderService


order_router = APIRouter()
order_service = OrderService()
role_checker = Depends(RoleChecker([UserRole.USER, UserRole.ADMIN]))


@order_router.post("/", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_order(order_data: OrderCreateSchema, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> OrderResponseSchema:
    user_id = current_user.id

    order = await order_service.create_order(user_id, order_data, session)

    if order is None:
        raise DatabaseException(
            message="Something went wrong.",
            details={}
        )

    return order

@order_router.get("/{order_id}", response_model=OrderResponseSchema, status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_order(order_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> OrderResponseSchema:

    order = await order_service.get_order_by_id(order_id, session)

    if order is None:
        raise DatabaseException(
            message="Something went wrong.",
            details={}
        )
    
    return order

@order_router.get("/", response_model=list[OrderResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_orders(session: AsyncSession = Depends(get_session)) -> list[OrderResponseSchema]:

    orders = await order_service.get_all_order(session)
    
    if orders is None:
        raise DatabaseException(
            message="Something went wrong.",
            details={}
        )
    
    return orders