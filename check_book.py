from __future__ import annotations

from api._books_store import search_books
from api._common import ApiError, ApiHandler


class handler(ApiHandler):
    def do_POST(self) -> None:
        try:
            data = self.read_json_body()
            title = str(data.get("title", "")).strip()
            author = str(data.get("author", "")).strip()

            if not title:
                raise ApiError("Titel is verplicht om te controleren.", 400)

            results = search_books(title, author)
            self.send_json(
                {
                    "exists": results["exact_match"],
                    "book": results["book"],
                    "exact_match": results["exact_match"],
                    "candidates": results["candidates"],
                }
            )
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
