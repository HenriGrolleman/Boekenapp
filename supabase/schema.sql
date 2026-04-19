create table if not exists public.books (
    id bigint generated always as identity primary key,
    title text not null,
    author text not null,
    normalized_title text not null,
    normalized_author text not null,
    purchase_date date,
    status text not null default 'owned',
    rating integer,
    review text,
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    started_reading_at timestamptz,
    finished_at timestamptz,
    constraint books_status_check check (status in ('owned', 'reading', 'finished')),
    constraint books_rating_check check (rating is null or rating between 1 and 5)
);

create unique index if not exists books_unique_normalized_idx
on public.books (normalized_title, normalized_author);

create index if not exists books_status_idx
on public.books (status);

create index if not exists books_title_idx
on public.books (normalized_title);

alter table public.books enable row level security;

drop policy if exists "No direct access" on public.books;
create policy "No direct access"
on public.books
for all
to anon, authenticated
using (false)
with check (false);
