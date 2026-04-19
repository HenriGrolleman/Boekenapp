from __future__ import annotations

from api._books_store import add_book, find_book, list_books
from api._common import ApiError, ApiHandler


class handler(ApiHandler):
    def do_GET(self) -> None:
        try:
            self.send_json({"books": list_books()})
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)

    def do_POST(self) -> None:
        try:
            data = self.read_json_body()
            title = str(data.get("title", "")).strip()
            author = str(data.get("author", "")).strip()
            purchase_date = str(data.get("purchase_date", "")).strip() or None

            if not title or not author:
                raise ApiError("Titel en auteur zijn verplicht.", 400)

            if find_book(title, author):
                raise ApiError("Dit boek staat al in je lijst.", 409)

            book = add_book(title, author, purchase_date)
            self.send_json({"book": book}, 201)
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
