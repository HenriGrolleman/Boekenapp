from __future__ import annotations

from api._books_store import find_book
from api._common import ApiError, ApiHandler


class handler(ApiHandler):
    def do_POST(self) -> None:
        try:
            data = self.read_json_body()
            title = str(data.get("title", "")).strip()
            author = str(data.get("author", "")).strip()

            if not title or not author:
                raise ApiError("Titel en auteur zijn verplicht om te controleren.", 400)

            book = find_book(title, author)
            self.send_json({"exists": book is not None, "book": book})
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
