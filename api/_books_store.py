from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from api._common import ApiError


BOOK_FIELDS = (
    "id,title,author,purchase_date,status,rating,review,"
    "created_at,updated_at,started_reading_at,finished_at"
)
STATUS_ORDER = {"reading": 0, "owned": 1, "finished": 2}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_value(value: str) -> str:
    return " ".join(value.strip().lower().split())


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ApiError(
            f"Serverconfiguratie mist {name}. Voeg deze variabele toe in Vercel.",
            500,
        )
    return value


def supabase_request(method: str, path: str, query=None, payload=None, prefer: str | None = None):
    base_url = require_env("SUPABASE_URL").rstrip("/")
    service_role_key = require_env("SUPABASE_SERVICE_ROLE_KEY")

    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"

    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Accept": "application/json",
    }
    data = None

    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    if prefer:
        headers["Prefer"] = prefer

    request = Request(url, data=data, method=method, headers=headers)

    try:
        with urlopen(request) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return None
            return json.loads(raw)
    except HTTPError as exc:
        raw_error = exc.read().decode("utf-8", errors="ignore")
        message = "Databaseverzoek mislukt."
        if raw_error:
            try:
                parsed = json.loads(raw_error)
                message = (
                    parsed.get("message")
                    or parsed.get("error_description")
                    or parsed.get("hint")
                    or message
                )
            except json.JSONDecodeError:
                message = raw_error
        raise ApiError(message, exc.code) from exc
    except URLError as exc:
        raise ApiError("Kan geen verbinding maken met de online database.", 502) from exc


def serialize_list(raw_books):
    return sorted(
        raw_books,
        key=lambda book: (
            STATUS_ORDER.get(book.get("status", "owned"), 99),
            str(book.get("title", "")).lower(),
        ),
    )


def list_books():
    response = supabase_request("GET", "/rest/v1/books", query={"select": BOOK_FIELDS})
    return serialize_list(response or [])


def find_book(title: str, author: str):
    response = supabase_request(
        "GET",
        "/rest/v1/books",
        query={
            "select": BOOK_FIELDS,
            "normalized_title": f"eq.{normalize_value(title)}",
            "normalized_author": f"eq.{normalize_value(author)}",
            "limit": "1",
        },
    )
    return response[0] if response else None


def add_book(title: str, author: str, purchase_date: str | None):
    clean_title = title.strip()
    clean_author = author.strip()
    now = utc_now_iso()
    response = supabase_request(
        "POST",
        "/rest/v1/books",
        payload={
            "title": clean_title,
            "author": clean_author,
            "normalized_title": normalize_value(clean_title),
            "normalized_author": normalize_value(clean_author),
            "purchase_date": purchase_date or None,
            "status": "owned",
            "created_at": now,
            "updated_at": now,
        },
        prefer="return=representation",
    )
    if not response:
        raise ApiError("Boek kon niet worden opgeslagen.", 502)
    return response[0]


def get_book(book_id: int):
    response = supabase_request(
        "GET",
        "/rest/v1/books",
        query={"id": f"eq.{book_id}", "select": BOOK_FIELDS, "limit": "1"},
    )
    return response[0] if response else None


def mark_as_reading(book_id: int):
    now = utc_now_iso()
    existing = get_book(book_id)
    if not existing:
        return None

    response = supabase_request(
        "PATCH",
        "/rest/v1/books",
        query={"id": f"eq.{book_id}", "select": BOOK_FIELDS},
        payload={
            "status": "reading",
            "updated_at": now,
            "started_reading_at": existing.get("started_reading_at") or now,
            "rating": None,
            "review": None,
            "finished_at": None,
        },
        prefer="return=representation",
    )
    return response[0] if response else None


def mark_as_finished(book_id: int, rating: int, review: str):
    now = utc_now_iso()
    existing = get_book(book_id)
    if not existing:
        return None

    response = supabase_request(
        "PATCH",
        "/rest/v1/books",
        query={"id": f"eq.{book_id}", "select": BOOK_FIELDS},
        payload={
            "status": "finished",
            "rating": rating,
            "review": review.strip(),
            "updated_at": now,
            "finished_at": now,
            "started_reading_at": existing.get("started_reading_at") or now,
        },
        prefer="return=representation",
    )
    return response[0] if response else None
