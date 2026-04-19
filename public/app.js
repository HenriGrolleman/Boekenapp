const bookListElement = document.getElementById("book-list");
const checkForm = document.getElementById("check-form");
const addForm = document.getElementById("add-form");
const checkResult = document.getElementById("check-result");
const addResult = document.getElementById("add-result");
const finishTemplate = document.getElementById("finish-template");


async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Er ging iets mis.");
  }

  return payload;
}


function setFeedback(element, message, type = "") {
  element.textContent = message;
  element.className = `feedback ${type}`.trim();
}


function formatDate(value) {
  if (!value) {
    return "Geen datum vastgelegd";
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-").map(Number);
    return new Intl.DateTimeFormat("nl-NL", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    }).format(new Date(year, month - 1, day));
  }

  return new Intl.DateTimeFormat("nl-NL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(new Date(value));
}


function renderStats(books) {
  document.getElementById("total-count").textContent = books.length;
  document.getElementById("reading-count").textContent = books.filter(
    (book) => book.status === "reading",
  ).length;
  document.getElementById("finished-count").textContent = books.filter(
    (book) => book.status === "finished",
  ).length;
}


function renderBooks(books) {
  renderStats(books);

  if (!books.length) {
    bookListElement.innerHTML =
      '<p class="empty-state">Je lijst is nog leeg. Voeg je eerste boek toe om te beginnen.</p>';
    return;
  }

  bookListElement.innerHTML = "";

  books.forEach((book) => {
    const item = document.createElement("article");
    item.className = "book-item";

    const statusLabel =
      book.status === "reading"
        ? "Aan het lezen"
        : book.status === "finished"
          ? "Uitgelezen"
          : "In kast";

    item.innerHTML = `
      <div class="book-meta">
        <div>
          <h3 class="book-title">${escapeHtml(book.title)}</h3>
          <p class="book-author">${escapeHtml(book.author)}</p>
          <p class="book-detail">Aankoopdatum: ${escapeHtml(formatDate(book.purchase_date))}</p>
        </div>
        <span class="book-status ${book.status}">${statusLabel}</span>
      </div>
    `;

    const actions = document.createElement("div");
    actions.className = "book-actions";

    if (book.status !== "reading") {
      const readingButton = document.createElement("button");
      readingButton.className = "secondary";
      readingButton.textContent = "Markeer als aan het lezen";
      readingButton.addEventListener("click", async () => {
        await markAsReading(book.id);
      });
      actions.appendChild(readingButton);
    }

    if (book.status !== "finished") {
      const finishToggle = document.createElement("button");
      finishToggle.className = "accent";
      finishToggle.textContent = "Afronden met review";
      finishToggle.addEventListener("click", () => {
        const existing = item.querySelector(".finish-form");
        if (existing) {
          existing.remove();
          finishToggle.textContent = "Afronden met review";
          return;
        }

        const form = finishTemplate.content.firstElementChild.cloneNode(true);
        form.addEventListener("submit", async (event) => {
          event.preventDefault();
          const formData = new FormData(form);
          await finishBook(book.id, {
            rating: Number(formData.get("rating")),
            review: String(formData.get("review") || ""),
          });
        });
        item.appendChild(form);
        finishToggle.textContent = "Sluit reviewformulier";
      });
      actions.appendChild(finishToggle);
    }

    if (actions.children.length) {
      item.appendChild(actions);
    }

    if (book.status === "finished") {
      const reviewBlock = document.createElement("div");
      reviewBlock.className = "review-block";
      reviewBlock.innerHTML = `
        <p class="stars">${"★".repeat(book.rating || 0)}${"☆".repeat(5 - (book.rating || 0))}</p>
        <p class="book-detail">${escapeHtml(book.review || "")}</p>
      `;
      item.appendChild(reviewBlock);
    }

    bookListElement.appendChild(item);
  });
}


function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}


async function loadBooks() {
  const payload = await requestJson("/api/books");
  renderBooks(payload.books);
}


async function markAsReading(bookId) {
  await requestJson(`/api/books/${bookId}/reading`, {
    method: "POST",
    body: JSON.stringify({}),
  });
  await loadBooks();
}


async function finishBook(bookId, data) {
  await requestJson(`/api/books/${bookId}/finish`, {
    method: "POST",
    body: JSON.stringify(data),
  });
  await loadBooks();
}


checkForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setFeedback(checkResult, "");
  const formData = new FormData(checkForm);

  try {
    const payload = await requestJson("/api/check-book", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title"),
        author: formData.get("author"),
      }),
    });

    if (payload.exists) {
      const label =
        payload.book.status === "reading"
          ? "Je bent dit boek nu aan het lezen."
          : payload.book.status === "finished"
            ? "Je hebt dit boek al uitgelezen."
            : "Dit boek staat al in je kast.";
      setFeedback(checkResult, label, "success");
    } else {
      setFeedback(checkResult, "Dit boek staat nog niet in je lijst.", "error");
    }
  } catch (error) {
    setFeedback(checkResult, error.message, "error");
  }
});


addForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setFeedback(addResult, "");
  const formData = new FormData(addForm);

  try {
    await requestJson("/api/books", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title"),
        author: formData.get("author"),
        purchase_date: formData.get("purchase_date"),
      }),
    });

    addForm.reset();
    setFeedback(addResult, "Boek toegevoegd aan je lijst.", "success");
    await loadBooks();
  } catch (error) {
    setFeedback(addResult, error.message, "error");
  }
});


loadBooks().catch((error) => {
  bookListElement.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
});
