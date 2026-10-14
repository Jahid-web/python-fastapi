from datetime import date

from src.models.book import Book
from src.models.category import Category
from src.models.author import Author

BOOK_API_CONFIG = {
    # Default sorting
    "default_sort": "created_at",
    "default_sort_order": "desc",

    # Maximum records returned per request
    "max_page_size": 100,

    # Search configuration
    "search_fields": [
        lambda term: Book.title.ilike(f"%{term}%"),
        lambda term: Book.author.has(
            Author.name.ilike(f"%{term}%")
        ),
    ],

    # Filter configuration
    "filter_fields": {
        "category_name": lambda value: Book.categories.any(
            Category.name == str(value)
        ),

        # "language": lambda value: (
        #     Book.language == value
        # ),

        "year": lambda value: (
            (Book.created_at >= date(int(value), 1, 1))
            & (
                Book.created_at
                < date(int(value) + 1, 1, 1)
            )
        ),
    },

    # Allowed sorting fields
    "sort_fields": {
        "created_at": Book.created_at,
        "title": Book.title,
        "Publication_date": Book.created_at,
    },
}
