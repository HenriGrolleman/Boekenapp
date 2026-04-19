# Boeken Register App

Webapp waarin je kunt bijhouden:

- welke boeken je hebt gekocht
- welke boeken je al hebt gelezen
- basisinformatie zoals titel, auteur, status en aankoopdatum
- een korte review met 1 t/m 5 sterren

## Functies

1. Controleren of een boek al bestaat op titel en auteur
2. Een nieuw boek toevoegen
3. Een boek markeren als "aan het lezen"
4. Een boek markeren als "uitgelezen" met rating en omschrijving

## Techniek

- Frontend: HTML, CSS en vanilla JavaScript
- Online hosting: Vercel
- Online database: Supabase Postgres
- Lokale variant: Python standaardbibliotheek + SQLite

## Online gebruiken

Voor gratis gebruik via internet is deze app ingericht voor:

- Vercel voor website en API-routes
- Supabase voor de persistente database

Belangrijk:

- dit draait gratis binnen de free tiers
- het is niet onbeperkt gratis zonder limieten

### Supabase instellen

1. Maak een gratis project aan in Supabase
2. Open de SQL Editor
3. Voer [supabase/schema.sql](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\supabase\schema.sql>) uit
4. Kopieer je project-URL en `service_role` key

### Vercel instellen

1. Maak een gratis Vercel-project aan op basis van deze map
2. Voeg de environment variables toe uit [.env.example](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\.env.example>)
3. Deploy de app

De online frontend staat in:

- [public/index.html](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\public\index.html>)
- [public/app.js](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\public\app.js>)
- [public/styles.css](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\public\styles.css>)

De online API-routes staan in:

- [api/books.py](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\api\books.py>)
- [api/check_book.py](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\api\check_book.py>)
- [api/book_status.py](<C:\Users\hg0108775\OneDrive - Windesheim Office365\Codex\boeken-register-app\api\book_status.py>)

## Lokale versie starten

Open een terminal in deze map en start:

```powershell
python app.py
```

Of dubbelklik op:

```text
start-boekenregister.cmd
```

Ga daarna naar:

```text
http://127.0.0.1:8000
```
.
