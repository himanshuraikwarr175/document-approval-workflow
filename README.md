# Document Approval Workflow

A small full-stack app for submitting a document and reviewing it. A submitter sends a document, a reviewer approves or rejects it, and the submitter can see the status change.

The app is meant to run locally. It is not hosted on a public URL.

## Setup

Requires Python 3.10+ and Node.js 20+.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

On startup the app creates `backend/document.db` (SQLite) and, if the users table is empty, inserts two demo users:

| id | name | email | role |
|---|---|---|---|
| 1 | himanshu test submitter | submitter@example.com | submitter |
| 2 | himanshu test reviewer | reviewer@example.com | reviewer |

If you change those names in `backend/app/seed.py` after the file already exists, delete `backend/document.db` and start the server again. The seed does not overwrite existing rows.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The header switches between the two demo users. The choice is stored in `localStorage`. The React app calls the API with an `X-User-Id` header (`1` or `2`).

## API design

Every submission call needs `X-User-Id`. A missing or non-numeric header returns `422`. An unknown id returns `401`.

One collection was enough. Create, list, and decide are all on `/api/submissions`. Submitters are automatically limited to their own rows, so a separate `/mine` resource was unnecessary. Reviewers can narrow the same list with `status`.

### `POST /api/submissions`

Submitter only. Multipart form with `title` and `file`. Creates a row with status `pending` and stores the file on disk. Allowed types are pdf, txt, png, jpg, jpeg, doc, and docx, up to 5 MB.

`201` returns the submission. A reviewer who calls this gets `403`. A blank title, an empty file, or a disallowed type gets `422`.

### `GET /api/submissions/{id}/file`

Downloads the uploaded file. A submitter can download only their own file (`403` otherwise). A reviewer can download any submission. A missing file returns `404`.

### `GET /api/submissions`

Query parameters:

- `status` — optional, one of `pending`, `approved`, `rejected`
- `mine` — optional boolean. When true, only the current user's rows are returned

A submitter always sees only their own submissions, even without `mine=true`. A reviewer sees every matching row. Results are newest first.

### `PATCH /api/submissions/{id}`

Reviewer only. Body:

```json
{ "status": "approved", "note": "Looks good" }
```

`status` must be `approved` or `rejected`. `note` is optional; a blank note is stored as `null`.

`200` returns the updated submission. A submitter gets `403`. An unknown id gets `404`. A document that is already approved or rejected gets `409`, because the only legal moves are `pending -> approved` and `pending -> rejected`.

### Submission response

```json
{
  "id": 1,
  "title": "Q3 report",
  "original_filename": "report.pdf",
  "status": "pending",
  "submitter_id": 1,
  "reviewer_note": null,
  "created_at": "2026-09-30T12:00:00Z",
  "updated_at": "2026-09-30T12:00:00Z"
}
```

## Major decisions

**Data model.** Two tables. `users` holds name, email, and role (`submitter` or `reviewer`). `submissions` holds title, the original filename, a stored file name, status, optional reviewer note, submitter id, and timestamps. The file bytes live in `backend/uploads`, which is gitignored. SQLite only stores the metadata.

**Status transitions.** New submissions start at `pending`. Only a reviewer can move them, and only once. The rule lives in `backend/app/services/submissions.py`. The HTTP layer only maps those failures to status codes.

**Identity.** There is no login. The UI picks one of the seeded users and sends `X-User-Id`. That is enough to demo both roles inside the time budget. It is not authentication.

**Storage.** SQLite in `backend/document.db`, gitignored. Uploaded files are in `backend/uploads`, also gitignored. An older database that still has a text `body` column is rebuilt for file metadata on startup. Tests use an in-memory database and a temporary upload folder.

**Modules.** Schemas validate payloads, services hold the rules, and routers stay thin. That split made the review rule testable without standing up the whole server for each case.

## Tests

From the repository root, with the backend virtualenv active:

```bash
cd backend
source .venv/bin/activate
cd ..
pytest
```

`pytest` from `backend/` also works. The suite covers create, list, approve, and the error cases (`401`, `403`, `404`, `409`, `422`).

## AI tools

Cursor was used to scaffold the FastAPI modules, the pytest suite, and the React client, and to debug the test import path. Seed names and git commits were handled manually. Be ready to walk through those pieces in the video and later rounds.

## Video walkthrough

Replace this line with the Loom (or similar) link:

`TODO: add video walkthrough URL`

## Production next steps

- Real authentication and roles, instead of a trusted user id header
- Object storage for uploads, instead of a local folder
- Postgres, migrations, and an audit log of status changes
- Pagination and assignment of a reviewer
- A public deployment, with the live URL added here
