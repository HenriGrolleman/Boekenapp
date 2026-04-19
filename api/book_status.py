from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from api._books_store import mark_as_finished, mark_as_reading
from api._common import ApiError, ApiHandler


class handler(ApiHandler):
    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            action = params.get("action", [""])[0]
            raw_id = params.get("id", [""])[0]

            if not raw_id.isdigit():
                raise ApiError("Ongeldig boek-id.", 400)

            book_id = int(raw_id)

            if action == "reading":
                book = mark_as_reading(book_id)
            elif action == "finish":
                data = self.read_json_body()
                rating = data.get("rating")
                review = str(data.get("review", "")).strip()

                if not isinstance(rating, int) or not 1 <= rating <= 5:
                    raise ApiError("Geef een rating van 1 t/m 5.", 400)
                if not review:
                    raise ApiError("Voeg een korte omschrijving toe.", 400)

                book = mark_as_finished(book_id, rating, review)
            else:
                raise ApiError("Onbekende statusactie.", 404)

            if not book:
                raise ApiError("Boek niet gevonden.", 404)

            self.send_json({"book": book})
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
