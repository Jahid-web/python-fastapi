# BOOK_API_CONFIG = {
#     # Default sorting
#     "default_sort": "created_at",
#     "default_sort_order": "desc",

#     # Maximum records returned per request
#     "max_page_size": 100,

#     # Search configuration
#     "search_fields": [
#         lambda term: Book.title.ilike(f"%{term}%"),
#         lambda term: Book.isbn.ilike(f"%{term}%"),
#         lambda term: Book.author.has(
#             Author.name.ilike(f"%{term}%")
#         ),
#     ],

#     # Filter configuration
#     "filter_fields": {
#         "category_id": lambda value: Book.categories.any(
#             Category.id == int(value)
#         ),

#         "language": lambda value: (
#             Book.language == value
#         ),

#         "year": lambda value: (
#             (Book.publication_date >= date(int(value), 1, 1))
#             & (
#                 Book.publication_date
#                 < date(int(value) + 1, 1, 1)
#             )
#         ),
#     },

#     # Allowed sorting fields
#     "sort_fields": {
#         "created_at": Book.created_at,
#         "title": Book.title,
#         "publication_date": Book.publication_date,
#     },
# }



# class APIFeatures:
#     def __init__(
#         self,
#         statement: Select,
#         *,
#         params: Mapping[str, Any],
#         config: Mapping[str, Any],
#         stable_sort: Any = None,
#     ):
#         self.statement = statement
#         self.params = params
#         self.config = config
#         self.stable_sort = stable_sort

#         self.page = max(1, int(params.get("page", 1)))

#         max_page_size = config.get("max_page_size", 100)
#         requested_size = int(params.get("page_size", 20))

#         self.page_size = min(
#             max(1, requested_size),
#             max_page_size,
#         )

#     def search(self) -> "APIFeatures":
#         term = self.params.get("search")

#         if not term or not str(term).strip():
#             return self

#         search_fields: Sequence[SearchFactory] = (
#             self.config.get("search_fields", [])
#         )

#         if search_fields:
#             term = str(term).strip()

#             self.statement = self.statement.where(
#                 or_(*(field(term) for field in search_fields))
#             )

#         return self

#     def filter(self) -> "APIFeatures":
#         filter_fields: Mapping[str, FilterFactory] = (
#             self.config.get("filter_fields", {})
#         )

#         for name, factory in filter_fields.items():
#             value = self.params.get(name)

#             if value is None or value == "":
#                 continue

#             self.statement = self.statement.where(factory(value))

#         return self

#     def sort(self) -> "APIFeatures":
#         sort_fields = self.config["sort_fields"]

#         sort_by = (
#             self.params.get("sort_by")
#             or self.config.get("default_sort", "created_at")
#         )

#         # Ignore unsupported fields and use the configured default.
#         column = sort_fields.get(
#             sort_by,
#             sort_fields[self.config.get("default_sort", "created_at")],
#         )

#         sort_order = str(
#             self.params.get(
#                 "sort_order",
#                 self.config.get("default_sort_order", "desc"),
#             )
#         ).lower()

#         ordering = column.asc() if sort_order == "asc" else column.desc()

#         orderings = [ordering]

#         # A unique tie-breaker makes ordering more deterministic.
#         if self.stable_sort is not None:
#             orderings.append(self.stable_sort.desc())

#         self.statement = self.statement.order_by(*orderings)
#         return self

#     def paginate(self) -> "APIFeatures":
#         offset = (self.page - 1) * self.page_size

#         self.statement = self.statement.offset(offset).limit(
#             self.page_size
#         )

#         return self

#     async def execute(
#         self,
#         session: AsyncSession,
#     ) -> dict[str, Any]:
#         # Count records matching the filters before pagination.
#         count_statement = (
#             select(func.count())
#             .select_from(
#                 self.statement.order_by(None).subquery()
#             )
#         )

#         total = await session.scalar(count_statement) or 0

#         result = await session.execute(self.statement)
#         items = result.scalars().all()

#         total_pages = ceil(total / self.page_size) if total else 0

#         return {
#             "items": items,
#             "pagination": {
#                 "page": self.page,
#                 "page_size": self.page_size,
#                 "total": total,
#                 "total_pages": total_pages,
#                 "has_next": self.page < total_pages,
#                 "has_previous": self.page > 1,
#             },
#         }