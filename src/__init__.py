from fastapi import FastAPI

from src.core.exception_handlers import register_all_exceptions_handlers
from src.core.middleware import register_middleware
from src.routes.auth import auth_router
from src.routes.book import book_router
from src.routes.author import author_router




version = "v1"

description = """
This REST API is able to;
- Create Read Update And delete ....
"""

version_prefix = f"/api/{version}"

app = FastAPI(
    title="Rest API Project",
    description=description,
    version=version,
    license = "not yet",
    contact= {
        "name": "Md. Jahid Hossain",
        "email": "jahid.husain1@gmail.com"
    }
)


register_all_exceptions_handlers(app)
register_middleware(app)

app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(book_router, prefix=f"{version_prefix}/book", tags=["book"])
app.include_router(author_router, prefix=f"{version_prefix}/author", tags=["author"])