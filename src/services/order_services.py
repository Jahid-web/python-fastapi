import uuid
from sqlalchemy import select
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.exceptions import NotFoundException, ConflictException, BadRequestException, ValidationException
from src.models.order import Order, OrderItem
from src.models.book import Book
from src.schemas.order import OrderCreateSchema, OrderResponseSchema, OrderItemResponseSchema


class OrderService:
    # /api/v1/orders --- List the authenticated user's orders
    async def get_all_order(self, session: AsyncSession) -> Order:
        try:
            result = await session.execute(
                select(Order).options(
                    selectinload(Order.items)
                ).order_by(Order.created_at)
            )

            orders = result.scalars().all()
            return orders

        except Exception:
            await session.rollback()
            raise

    # /api/v1/orders/{order_id} ---- Get order details and line items
    async def get_order_by_id(self, order_id: str, session: AsyncSession) -> Order:
        try:
            result = await session.execute(
                select(Order).options(
                    selectinload(Order.user),
                    selectinload(Order.items)
                ).where(
                    Order.id == order_id
                )
            )

            order_item = result.scalar_one_or_none()
            return order_item

        except Exception:
            await session.rollback()
            raise
    
    # /api/v1/orders ---- Create an order with one or more books
    async def create_order(self, user_id: str, order_data: OrderCreateSchema, session: AsyncSession) -> OrderResponseSchema:
        try:
            quantities: dict[uuid.UUID, int] = {}

            for item in order_data.items:
                quantities[item.book_id] = (
                    quantities.get(item.book_id, 0) + item.quantity
                )

            if any(qty > 1000 for qty in quantities.values()):
                raise ValidationException(
                    message="Combined quantity for a book cannot exceed 1000.",
                    details={}
                )

            result = await session.execute(
                select(Book).where(
                    Book.id.in_(list(quantities.keys()))
                ).order_by(Book.created_at).with_for_update()
            )

            books = result.scalars().all()
            books_by_id = {book.id: book for book in books}

            missing_ids = set(quantities) - set(books_by_id)

            if missing_ids:
                raise NotFoundException(
                    message="One or more books do not exist.",
                    details={}
                )

            order_items: list[OrderItem] = []
            total_amount = Decimal("0.00")

            for book_id, quantity in quantities.items():
                book = books_by_id[book_id]

                if book.price is None or book.price < 0:
                    raise ConflictException(
                        message="A book has an invalid price.",
                        details={}
                    )

                if book.stock is None or book.stock < quantity:
                    raise ValidationException(
                        message="Insufficient stock for book.",
                        details=f"Book_ids: {book_id}"
                    )

                unit_price = Decimal(book.price).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP
                )

                line_total = unit_price * quantity
                total_amount += line_total

                order_items.append(
                    OrderItem(
                        book_id=book.id,
                        quantity=quantity,
                        price=unit_price
                    )
                )

                total_amount = total_amount.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP
                )

                order = Order(
                    user_id=user_id,
                    status="pending",
                    total_amount=total_amount,
                    items=order_items
                )

                for book_id, quantity in quantities.items():
                    books_by_id[book_id].stock -= quantity

                session.add(order)
                await session.commit()
                return order


        except Exception:
            await session.rollback()
            raise

    # /api/v1/orders/{order_id}/cancel ---- Cancel an eligible order
    async def cancel_order(self, user_id: str, order_id: str, session: AsyncSession) -> OrderResponseSchema:
        try:
            order = await session.execute(
                select(Order).where(
                    Order.id == order_id,
                    Order.user_id == user_id
                ).options(selectinload(Order.items))
                .with_for_update(of=Order)
            )

            if order is None:
                raise NotFoundException(
                    message="Order not found.",
                    details={}
                )

            if order.status not in {"pending", "confirmed"}:
                raise BadRequestException(
                    message=f"Order cannot be cancelled while its status is '{order.status}",                    
                )

            book_ids = {item.book_id for item in order.items}

            result = await session.execute(
                select(Book).where(
                    Book.id.in_(book_ids)
                ).order_by(Book.created_at).with_for_update()
            )
            books = result.scalars().all()

            books_by_id = {book.id: book for book in books}
            missing_ids = book_ids - set(books_by_id)

            if missing_ids:
                raise ValidationException(
                    message="Unable to restore inventory for this order.",
                    details={}
                )

            for item in order.items:
                book = books_by_id[item.book_id]
                book.stock += item.quantity

            order.status = "cancelled"

            session.add(order)
            await session.commit()

        except Exception:
            await session.rollback()
            raise

    # /api/v1/orders/{order_id}/items ---- List items in an order
    async def get_order_items(self, user_id: str, order_id: str, session: AsyncSession) -> list[OrderItemResponseSchema]:
        try:
            order = await session.execute(
                select(Order).where(
                    Order.id == order_id,
                    Order.user_id == user_id
                ).options(selectinload(Order.items))
            )

            if order is None:
                raise NotFoundException(
                    message="Order not found.",
                    details={}
                )

            order_item = [item for item in order.items]
            
            return order_item

        except Exception:
            await session.rollback()
            raise

