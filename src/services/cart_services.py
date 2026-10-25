import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio.session import AsyncSession
from decimal import Decimal

from src.models.book import Book
from src.db.main import get_session
from src.models.cart import Cart, CartItem
from src.core.exceptions import DatabaseException, ValidationException, NotFoundException, ConflictException

MAX_ITEM_QUANTITY = 100

class CartService:

    async def get_cart_by_user_id(self, user_id: uuid.UUID, session: AsyncSession) -> Cart:
        try:
            result = await session.execute(
                select(Cart)
                .where(Cart.user_id == user_id)
                .options(
                    selectinload(Cart.items).joinedload(CartItem.book)
                )
            )
            cart = result.scalar_one_or_none()

            if cart is None:
                raise NotFoundException(
                    message="Cart not found.",
                    details={}
                )
            
            return cart
        except Exception:
            await session.rollback()
            raise

    #1.  Get my cart ==== GET /api/v1/cart ======= Retrieve cart, items, and totals
    async def get_or_create_user_cart(self, user_id: uuid.UUID, session: AsyncSession) -> Cart:
        try:
            cart = await self.get_cart_by_user_id(user_id, session)

            if cart is not None:
                return cart
            else:
                cart = Cart(user_id=uuid.UUID(user_id))
                session.add(cart)

                await session.flush()
                await session.commit()
                await session.refresh(cart)

                return cart

        except Exception:
            await session.rollback()            
            raise

        # cart = await get_cart_by_user_id(user_id)

        # if cart is None:
        #     raise DatabaseException(
        #         message="Unable to initialize cart.",
        #         details={}
        #     )
        # return cart

    #2. Get cart summary =======  GET /api/v1/cart/summary =======  Retrieve item count and subtotal
    async def get_summary(self, user_id: str, session: AsyncSession) -> dict:
        try:
            cart = await self._locked_cart(user_id, session)

            total_items = sum(item.quantity for item in cart.items)
            subtotal = sum(
                (
                    Decimal(str(item.book.price)) * item.quantity for item in cart.items
                ),
                start=Decimal("0.00")
            )

            return {
                "cart_id": cart.id,
                "total_items": total_items,
                "distinct_books": len(cart.items),
                "subtotal": subtotal
            }

        except Exception:
            await session.rollback()
            raise


    async def _locked_cart(self, user_id: uuid.UUID, session: AsyncSession) -> Cart:
        try:
            result = await session.execute(
                select(Cart)
                .where(Cart.user_id == user_id)
                .options(selectinload(Cart.items).selectinload(CartItem.book))
                .with_for_update()
            )
            cart = result.scalar_one_or_none()

            if cart is None:
                # raise NotFoundException(
                #     message="Cart not found.",
                #     details={}
                # )
                cart = Cart(user_id=user_id)
                session.add(cart)
                await session.flush()

            return cart

        except Exception:
            await session.rollback()
            raise

    async def _load_cart(self, user_id: uuid.UUID, session: AsyncSession) -> Cart:
        try:
            cart = await self.get_cart_by_user_id(user_id, session)

            if cart is None:
                return await self.get_or_create_user_cart(user_id, session)
            
            return cart

        except Exception:
            await session.rollback()
            raise
    
    #3. Add item  ======= POST /api/v1/cart/items =======  Add a book or increase its quantity
    async def add_item(self, user_id: uuid.UUID, book_id: uuid.UUID, session: AsyncSession, qty: int = 1) -> Cart:
        try:
            if qty < 1 or qty > MAX_ITEM_QUANTITY:
                raise ValidationException(
                    message=f"Quantity must be between 1 and {MAX_ITEM_QUANTITY}.",
                    details={}
                )

            
            cart = await self._locked_cart(user_id, session)

            book_result = await session.execute(
                select(Book).where(Book.id == book_id).with_for_update()
            )
            book = book_result.scalar_one_or_none()

            if book is None:
                raise NotFoundException(
                    message="Book not found.",
                    details={}
                )

            if book.stock < 1:
                raise ConflictException(
                    message="Book is out of stock.",
                    details={}
                )

            item_result = await session.execute(
                select(CartItem).where(
                    CartItem.cart_id == cart.id,
                    CartItem.book_id == book_id
                )
            )
            item = item_result.scalar_one_or_none()

            new_qty = qty + (item.quantity if item else 0)

            if new_qty > MAX_ITEM_QUANTITY:
                raise ConflictException(
                    message="Maximum item quantity exceeded.",
                    details={}
                )

            if new_qty > book.stock:
                raise ConflictException(
                    message="Requested quantity exceeds available stock.",
                    details={}
                )

            if item:
                item.quantity = new_qty
            else:
                session.add(
                    CartItem(
                        cart_id=cart.id,
                        book_id=book_id,
                        quantity=qty
                    )
                )
            await session.commit()
            # return await self._locked_cart(user_id, session)
            result = await session.execute(
                select(Cart).where(
                    Cart.user_id == user_id
                ).options(
                    selectinload(Cart.items)
                )
            )
            return result.scalar_one_or_none()

        except Exception:
            await session.rollback()
            raise

    #4. Get cart items =======  GET /api/v1/cart/items =======  List items with pagination 
    async def get_cart(self, user_id: str, session: AsyncSession) -> Cart:
            try:
                cart = await self._load_cart(user_id, session)
                return cart
    
            except Exception:
                await session.rollback()
                raise
    
    #5. Get one cart item =======  GET /api/v1/cart/items/{item_id} =======  Retrieve a specific item 
    
    #6. Update quantity =======  PATCH /api/v1/cart/items/{item_id} =======  Set a new quantity 
    async def update_item(self, user_id: str, item_id: str, qty: int, session: AsyncSession) -> Cart:
        try:
            if qty < 1 or qty > MAX_ITEM_QUANTITY:
                raise ValidationException(
                    message=f"Quantity must be between 1 and {MAX_ITEM_QUANTITY}.",
                    details={}
                )
            cart = await self._locked_cart(user_id, session)

            result = await session.execute(
                select(CartItem).where(
                    CartItem.id == item_id,
                    CartItem.cart_id == cart.id
                ).with_for_update()
            )
            item = result.scalar_one_or_none()

            if item is None:
                raise NotFoundException(
                    message="Cart item not found.",
                    details={}
                )

            book_result = await session.execute(
                select(Book).where(Book.id == item.book_id)
            )
            book = book_result.scalar_one_or_none()

            if book is None:
                raise ConflictException(
                    message="The book associated with this item no longer exists.",
                    details={}
                )

            if qty > book.stock:
                raise ConflictException(
                    message="Requested quantity exceeds available stock.",
                    details={}
                )
            item.quantity = qty
            await session.commit()

            return await self._load_cart(user_id, session)

        except Exception:
            await session.rollback()
            raise

    
    #7. Increment quantity =======  POST /api/v1/cart/items/{item_id}/increment =======  Increase quantity 
    #8. Decrement quantity =======  POST /api/v1/cart/items/{item_id}/decrement =======  Decrease quantity 
    async def change_qty(self, user_id: str, item_id: str, delta: int, session: AsyncSession) -> Cart:
            try:
                if delta not in (-1, 1):
                    raise ValueError("delta must be either 1 or -1.")

                cart = await self._locked_cart(user_id, session)
    
                result = await session.execute(
                    select(CartItem).where(
                        CartItem.id == item_id,
                        CartItem.cart_id == cart.id
                    ).with_for_update()
                )
                item = result.scalar_one_or_none()
    
                if item is None:
                    raise NotFoundException(
                        message="Cart item not found.",
                        details={}
                    )
                new_qty = item.quantity + delta
    
                if new_qty < 1:
                    raise ConflictException(
                        message="Quantity cannot be less than one. Remove the item instead.",
                        details={}
                    )
    
                book_result = await session.execute(
                    select(Book).where(Book.id == item.book_id)
                )
                book = book_result.scalar_one_or_none()
    
                if book is None or new_qty > book.stock:
                    raise ConflictException(
                        message="Requested quantity is not available.",
                        details={}
                    )
    
                item.quantity = new_qty
                await session.commit()
    
                return await self._load_cart(user_id, session)
    
            except Exception:
                await session.rollback()
                raise
    
    #9. Remove item =======  DELETE /api/v1/cart/items/{item_id}  ======= Remove one book 
    async def remove_item(self, user_id: str, item_id: str, session: AsyncSession) -> None:
        try:
            cart = await self._load_cart(user_id, session)

            result = await session.execute(
                select(CartItem).where(
                    CartItem.id == item_id,
                    CartItem.cart_id == cart.id
                )
            )
            item = result.scalar_one_or_none()

            if item is None:
                raise NotFoundException(
                    message="Cart item not found.",
                    details={}
                )

            await session.delete(item)
            await session.commit()

        except Exception:
            await session.rollback()
            raise

    #10. Clear cart =======  DELETE /api/v1/cart/items =======  Remove all cart items 
    async def clear_cart(self, user_id: str, session: AsyncSession) -> None:
        try:
            cart = await self._locked_cart(user_id, session)

            result = await session.execute(
                select(Cart).where(
                    Cart.id == cart.id
                )
            )
            items = result.scalars().all()

            for item in items:
                await session.delete(item)

            await session.commit()

        except Exception:
            await session.commit()
            raise
        
    #11. Merge guest cart =======  POST /api/v1/cart/merge  ======= Merge an anonymous cart after login 
    #12 Validate cart =======  POST /api/v1/cart/validate  ======= Check stock and purchase eligibility
    async def validate_cart(self, user_id: str, session: AsyncSession) -> dict:
        try:
            cart = await self._locked_cart(user_id, session)

            issues = []

            for item in cart.items:
                book = item.book

                if book is None:
                    issues.append({
                        "book_id": item.book_id,
                        "message": "Book no longer exists."
                    })
                    continue

                if book.stock < item.quantity:
                    issues.append({
                        "book_id": item.book_id,
                        "message": (
                            f"Requested quantity {item.quantity} exceeds"
                            f"available stock {book.stock}"
                        )
                    })

            return {
                "valid": not issues,
                "issues": issues
            }

        except Exception:
            await session.rollback()
            raise