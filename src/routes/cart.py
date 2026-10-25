from fastapi import APIRouter, status, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.models.user import UserRole, User
from src.services.cart_services import CartService
from src.schemas.cart import CartItemCreateSchema, CartItemUpdateSchema, CartReadSchema, CartSummarySchema, CartValidationResultSchema
from src.utils.dependencies import get_current_user, RoleChecker


cart_router = APIRouter()
role_checker = Depends(RoleChecker([UserRole.ADMIN, UserRole.USER]))
cart_service = CartService()


@cart_router.get("/", response_model= CartReadSchema, status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_cart(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> CartReadSchema:
    user_id = current_user.id

    return await cart_service.get_cart(user_id, session)


@cart_router.get("/summary", response_model=CartSummarySchema, status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_summary(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> CartSummarySchema:
    user_id = current_user.id

    return await cart_service.get_summary(user_id, session)

@cart_router.get("/item", response_model=CartReadSchema, status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_cart_items(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> CartReadSchema:
    user_id = current_user.id

    cart = await cart_service.get_cart(user_id, session)
    return cart

@cart_router.post("/items", response_model=CartReadSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def add_cart_item(cart_data: CartItemCreateSchema, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> CartReadSchema:
    user_id = current_user.id
    book_id = cart_data.book_id
    qty = cart_data.quantity

    return await cart_service.add_item(user_id, book_id, session, qty)

@cart_router.patch("/items/{item_id}", response_model=CartReadSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def update_cart_item(cart_data: CartItemUpdateSchema, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    book_id = cart_data.book_id
    qty = cart_data.quantity

    return await cart_service.update_item(user_id, book_id, qty, session)


@cart_router.post("/items/{item_id}/increment", response_model=CartReadSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def increment_cart_item(item_id: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    delta = 1

    return await cart_service.change_qty(user_id, item_id, delta, session)

@cart_router.post("/items/{item_id}/decrement", response_model=CartReadSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def decrement_cart_item(item_id: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    delta = -1

    return await cart_service.change_qty(user_id, item_id, delta, session)

@cart_router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def remove_cart_item(item_id: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id

    await cart_service.remove_item(user_id, item_id, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@cart_router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def clear_cart(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id

    await cart_service.clear_cart(user_id, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cart_router.post("/validate", response_model=CartValidationResultSchema, dependencies=[role_checker])
async def validate_cart(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id

    return await cart_service.validate_cart(user_id, session)


