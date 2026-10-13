from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from math import ceil
from typing import Any
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

FilterFactory = Callable[[Any], ColumnElement[bool]]
SearchFactory = Callable[[str], ColumnElement[bool]]

@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        return ceil(self.total / self.page_size) if self.total else 0

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

class APIFeatures:
    def __init__(
            self,
            statement: Select,
            *,
            params: Mapping[str, Any],
            search_fields: Sequence[SearchFactory] = (),
            filter_fields: Mapping[str, FilterFactory] | None = None,
            sort_fields: Mapping[str, Any] | None = None,
            default_sort: str = "created_at",
            stable_sort: Any = None,
            max_page_size: int = 100
    ):
        self.statement = statement
        self.filtered_statement = statement
        
        self.params = params
        self.search_fields = search_fields
        self.filter_fields = filter_fields or {}
        self.sort_fields = sort_fields or {}
        self.default_sort = default_sort
        self.stable_sort = stable_sort
        self.max_page_size = max_page_size

        self.page = max(1, int(params.get("page", 1)))
        self.page_size = min(
            max(1, int(params.get("page_size", 20))),
            max_page_size
        )


    def search(self) -> "APIFeatures":
        term = self.params.get("search")

        if term and str(term).strip() and self.search_fields:
            term = str(term).strip()

            conditions = [
                factory(term) for factory in self.search_fields
            ]
            self.filtered_statement = (
                self.filtered_statement.where(or_(*conditions))
            )

        return self

    def filter(self) -> "APIFeatures":
        for name, factory in self.filter_fields.items():
            value = self.params.get(name)

            if value is None or value == "":
                continue

            self.filtered_statement = (
                self.filtered_statement.where(factory(value))
            )

        return self

    def sort(self) -> "APIFeatures":
        requested = self.params.get("sort_by") or self.default_sort
        column = self.sort_fields.get(requested)

        if column is None:
            column = self.sort_fields[self.default_sort]

        direction = str(
            self.params.get("sort_order", "desc")
        ).lower()

        ordering = column.asc() if direction == "asc" else column.desc()

        orderings = [ordering]

        if self.stable_sort is not None:
            orderings.append(self.stable_sort.desc())

        self.statement = self.filtered_statement.order_by(
            *orderings
        )
        return self

    def paginate(self) -> "APIFeatures":
        offset = (self.page - 1) * self.page_size

        self.statement = self.statement.offset(offset).limit(
            self.page_size
        )
        return self

    async def execute(self, session: AsyncSession) -> dict[str, Any]:
        count_statement = (            
            select(func.count())
            .select_from(self.filtered_statement.order_by(None).subquery())
            )

        total = await session.scalar(count_statement) or 0
        result = await session.execute(self.statement)

        items = result.scalars().all()

        pagination = Pagination(
            page=self.page,
            page_size=self.page_size,
            total=total
        )


        return {
            "items": items,
            "pagination": {
                "page": pagination.page,
                "page_size": pagination.page_size,
                "total": pagination.total,
                "total_pages": pagination.total_pages,
                "has_next": pagination.page < pagination.total_pages,
                "has_previous": pagination.page > 1
            }
        }
