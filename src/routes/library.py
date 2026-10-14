from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.core.exceptions import NotFoundException, UnAuthorizedException, BadRequestException
from src.services.library_services import LibraryService
from src.models.user import UserRole
from src.schemas.library import LibResponseSchema, LibPurchaseSchema
from src.utils.dependencies import RoleChecker, get_current_user
from src.models.user import User


# Recommended additional features
# These features can build on the existing model, although some require additional models or fields.
# Automatic library creation after payment: Add purchased books to the library only after an order is successfully paid.
# Duplicate purchase prevention: Use the existing unique constraint to prevent duplicate entries for the same user and book.
# Secure book access: Verify library ownership before allowing access to protected book files or reading content.
# Download tracking: Record download counts and last download time in a separate table or additional fields.
# Reading progress: Track pages read, bookmarks, and completion status.
# Wishlist: Allow users to save books they do not own yet.
# Refund handling: Define whether refunded books should be removed from the library or marked as revoked.
# Admin reporting: Allow authorized administrators to inspect library entries and purchase associations.

lib_router = APIRouter()
lib_service = LibraryService()
role_checker = Depends(RoleChecker([UserRole.ADMIN, UserRole.USER]))

# 1. /api/v1/library === Get the authenticated user's library.
@lib_router.get("/", response_model=list[LibResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_all_lib(session: AsyncSession = Depends(get_session)):
    librarys = await lib_service.get_all_lib(session)

    if librarys is None:
        raise NotFoundException(
            message="No library found.",
            details={}
        )

    return librarys

# 2. /api/v1/library/{book_id} === Get a specific book in the user's library.
@lib_router.get("/{lib_id}", response_model=LibResponseSchema, status_code=status.HTTP_200_OK)
async def get_lib(lib_id: str, session: AsyncSession = Depends(get_session)):
    library = await lib_service.get_lib_by_id(lib_id, session)

    if library is None:
        raise NotFoundException(
            message="No library found.",
            details={}
        )

    return library

# 3. /api/v1/library/{book_id}/purchase === Get purchase details for a library book.
@lib_router.get("/{lib_id}/purchase", response_model=LibPurchaseSchema, status_code=status.HTTP_200_OK)
async def get_lib(lib_id: str, session: AsyncSession = Depends(get_session)):
    purchase_datails = await lib_service.get_lib_purchase_details(lib_id, session)

    if purchase_datails is None:
        raise NotFoundException(
            message="No purchase datails found.",
            details={}
        )

    return purchase_datails

# 4. /api/v1/library/check/{book_id} === Check whether the user owns a book.
# 5. /api/v1/library/count === Count the user's library books.
# 6. /api/v1/library/order/{order_id} === List library books associated with an order.
@lib_router.get("/order/{order_id}", response_model=LibPurchaseSchema, status_code=status.HTTP_200_OK)
async def get_lib_order( order_id: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user.id
    
    lib_order = await lib_service.get_lib_order(user_id, order_id, session)

    if lib_order is None:
        raise NotFoundException(
            message="No order datails found.",
            details={}
        )

    return lib_order
# 7. /api/v1/library/{book_id} === Remove a book from the user's library, if your business rules allow it.
