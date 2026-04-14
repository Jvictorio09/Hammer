# Insights Dynamic System Documentation

This document explains how the Insight dynamic system was built so you can replicate it in other projects.

## Scope

This documentation covers:

- `myProject/myApp/templates/dashboard/insight_form_new.html`
- `myProject/myApp/templates/dashboard/insight_form.html`
- `myProject/myApp/templates/dashboard/insight_import.html`
- `myProject/myApp/templates/dashboard/insights_list.html`

The main source of truth for current behavior is `insight_form_new.html`.  
`insight_form.html` is an earlier implementation with similar capabilities.

---

## 1) System Architecture (High Level)

The dynamic Insight system is made of 4 parts:

1. **List Page (`insights_list.html`)**
   - Search/filter insights.
   - Toggle cards/table views.
   - Open edit/delete/toggle-active actions.

2. **Editor Page (`insight_form_new.html`)**
   - Main authoring UI with Editor.js.
   - Autosave state handling.
   - Cover image preview and gallery integration.
   - Google Drive image import.
   - Document import (`.docx` / `.pdf`) to blocks.
   - Form submission guard to ensure blocks are serialized before submit.

3. **Legacy Editor (`insight_form.html`)**
   - Older editor flow.
   - Extra visualization experiments for blocks.
   - Useful for reference, but not primary baseline.

4. **Import Utility (`insight_import.html`)**
   - Server-driven page to convert existing HTML body content to Editor.js blocks.

---

## 2) Data Flow

### A) Editing and Saving

1. Server renders template with existing blocks in `data-blocks`.
2. Frontend parses `data-blocks` and initializes Editor.js.
3. On every change:
   - marks unsaved,
   - schedules autosave,
   - serializes blocks to hidden input (`#blocksField`).
4. On submit:
   - blocks are saved again (awaited),
   - hidden field is updated,
   - form is submitted.

### B) Media Selection

1. User can paste cover URL manually, or pick/upload/import from Drive.
2. On selection, cover URL field is updated.
3. Cover preview updates immediately.

### C) Document-to-Blocks

1. User uploads `.docx`/`.pdf`.
2. Backend converts document to Editor.js-compatible blocks.
3. Frontend renders returned blocks directly in editor.
4. Hidden blocks field is refreshed for submission.

---

## 3) `insight_form_new.html` - Full Function Reference

All functions below are inside `DOMContentLoaded`.

### Core Utility

- **`getCookie(name)`**
  - Reads cookie value by key.
  - Used to fetch CSRF token.

- **`polishInputs()` (IIFE)**
  - Applies UI classes to generated Django form controls.
  - Excludes title/excerpt main writing fields.
  - Adds checkbox styling.

### Editor Initialization and State

- **`initial` (IIFE variable builder)**
  - Reads JSON from `#blocksData[data-blocks]`.
  - Tries parse, validates shape (`blocks` array).
  - Falls back to empty Editor.js document.

- **`autoSave()`**
  - Prevents overlapping save operations (`isSaving` guard).
  - Calls `editor.save()`.
  - Updates hidden `#blocksField`.
  - Updates save status text.
  - Maintains unsaved flags.

- **`updateSaveStatus(status)`**
  - UI renderer for save banner.
  - Handles: `saving`, `saved`, `unsaved`, `error`, and default.

- **Editor `onChange` callback**
  - Sets unsaved state.
  - Debounces `autoSave()` (1 second).
  - Logs block/link diagnostics (debug support).

### Block Insertion

- **Add block click handler (`#addBlockBtn`)**
  - Reads current output.
  - Pushes an empty paragraph block.
  - Re-renders content.
  - Focuses last editable block.

### Title + Slug

- **`generateSlug(text)`**
  - lowercases,
  - removes special chars,
  - converts spaces/underscores to `-`,
  - trims leading/trailing `-`.

- **Title input listener**
  - Updates command bar title (`#currentTitle`).
  - Auto-populates slug (`input[name="slug"]`) up to 220 chars.

### Cover Preview

- **`updateCoverPreview()` (inner function)**
  - Validates `cover_image_url`.
  - Loads image with `new Image()`.
  - Shows/hides preview and fallback labels.

### Gallery Modal + Tabs

- **`openGallery()`**
  - Shows modal.
  - Sets default tab.
  - Triggers image fetch.

- **`closeGalleryModal()`**
  - Hides modal.

- **`switchToGalleryTab()` / `switchToUploadTab()` / `switchToGdriveTab()`**
  - Tab wrappers calling `activateTab`.

- **`activateTab(activeTab, activeContent)`**
  - Deactivates all tabs.
  - Hides all tab panels.
  - Activates target tab/panel.

- **`loadGalleryImages()`**
  - Fetches images from `gallery_api_images`.
  - Renders image cards.
  - Click on image updates cover URL and closes modal.
  - Handles empty/error states.

### Gallery Upload

- **`handleFileUpload(files)`**
  - Uploads selected files to `gallery_api_upload`.
  - Displays progress.
  - On success, refreshes gallery view.
  - On error, shows failure status.

### Google Drive Upload

- **Drive upload click handler (`#gdriveUploadBtn`)**
  - Validates Drive URL.
  - POSTs to `google_drive_upload` with `drive_url` and `auto_compress`.
  - Displays progress and status.
  - On success, sets cover image URL and closes modal.
  - On failure, shows error status.

### Preview Mode

- **Preview toggle click handler (`#previewToggle`)**
  - Opens/closes preview modal.
  - Saves current editor data before entering preview.
  - Uses placeholder preview rendering in this template.

- **Close preview handler (`#closePreview`)**
  - Closes modal and resets preview state.

### Submit Protection

- **Form submit handler (`#insightForm`)**
  - Prevents first submit.
  - Awaits `editor.save()` and writes `#blocksField`.
  - Uses `blocksSaved` flags to avoid infinite resubmit loop.
  - Re-submits form only after block JSON is synchronized.
  - Errors update save status and show alert.

### Unsaved Navigation Guard

- **`beforeunload` listener**
  - Warns user if there are unsaved changes.

### Editor Ready Hook

- **`editor.isReady.then(...)`**
  - Logs readiness (debug visibility).

### Document Import (`.docx` / `.pdf`)

- **Document button click (`#documentUploadBtn`)**
  - Triggers hidden file input.

- **Document input change handler**
  - Validates file type.
  - Uploads to `dashboard_insight_upload_document`.
  - Tracks progress.
  - On success:
    - updates title (if provided),
    - renders returned blocks in editor,
    - updates hidden blocks field,
    - updates save status.
  - On failure:
    - shows error state and resets progress UI.

---

## 4) `insight_form.html` (Legacy) - Function Map

This template contains similar behavior with extra experimental UI logic.

### Major functions

- `polishInputs()` - style default inputs.
- `getCookie(name)` - CSRF cookie.
- `enhanceBlockVisualization()` - decorates blocks with labels/separators.
- `ensureBottomEditable()` - attempts to keep final area editable/clickable.
- `debounce(fn, ms)` - generic debounce.
- `setSaved()` - updates autosave labels.
- `blink(btn)` - temporary template insertion confirmation.
- `looksLikeImage(url)` and `updateCoverPreview()` - cover preview.
- `openGallery()`, `closeGalleryModal()`, tab switch helpers, `activateTab()`.
- `loadGalleryImages()` and `handleFileUpload(files)`.
- Google Drive upload click handler.
- Form submit pre-save handler.
- Preview open/close handlers.
- Slash-command keydown and template insertion handlers.

### Replication note

If you replicate this system, start from `insight_form_new.html`, then only borrow specific pieces from this legacy file if needed.

---

## 5) `insights_list.html` - Function Reference

### Functions

- **`match(el, q, stat)`**
  - Returns whether a card/row should be visible based on search + status.

- **`apply()`**
  - Reads current filter values.
  - Applies visibility changes to cards and table rows.

- **`setView(v)`**
  - Toggles cards/table display.
  - Updates active button styles.
  - Persists user choice in `localStorage` (`insightsView`).

### Event bindings

- Search input `input` -> `apply`.
- Status filter `change` -> `apply`.
- Cards/Table buttons -> `setView`.
- Action menu buttons toggle each row/card menu.
- Keyboard `/` focuses search input if user is not typing in an input/textarea.

---

## 6) `insight_import.html` - Behavior

No client-side functions.

This page is server-driven:

- `convert_all` submit converts all pending insights.
- `insight_id` submit converts one selected insight.

Use this as an operational admin utility rather than dynamic JS behavior.

---

## 7) Backend Endpoints Required

The frontend depends on these endpoints:

- `editor_image_upload`
- `gallery_api_images`
- `gallery_api_upload`
- `google_drive_upload`
- `dashboard_insight_upload_document`
- standard create/edit insight form POST endpoint

Expected response patterns:

- Gallery list: `{ images: [...] }`
- Gallery upload: `{ success: bool, images?: [...], error?: str }`
- Drive upload: `{ success: bool, image?: {...}, error?: str }`
- Document upload: `{ success: bool, title?: str, blocks?: {...}, error?: str }`

---

## 8) Replication Checklist for Other Projects

Use this exact order to replicate safely:

1. **Model layer**
   - Add fields for title, excerpt, slug, cover URL, published flags, blocks JSON, metadata.

2. **Form layer**
   - Include hidden `blocks` input and visible `title`, `excerpt`, `cover_image_url`, etc.

3. **Template baseline**
   - Start from `insight_form_new.html`.
   - Keep IDs/names stable (`editorHost`, `blocksField`, `blocksData`, `insightForm`).

4. **Editor.js setup**
   - Include script dependencies.
   - Initialize with parsed JSON.
   - Ensure `onChange` serializes blocks into hidden input.

5. **Submission safety**
   - Keep submit interception that awaits `editor.save()` before actual submit.

6. **Media pipeline**
   - Implement gallery list/upload endpoints.
   - Implement Google Drive ingestion endpoint.
   - Wire cover image preview updates.

7. **Document import**
   - Implement doc/pdf conversion endpoint returning Editor.js blocks.
   - Render returned blocks into editor.

8. **List page UX**
   - Add search/filter + cards/table toggle + row actions.

9. **Validation + permissions**
   - Validate URLs, file types, and user permissions server-side.
   - Do not rely only on frontend guards.

10. **Production hardening**
   - Remove noisy debug `console.log` messages.
   - Add error toasts/messages and retry handling.
   - Add tests for endpoint response shapes.

---

## 9) Recommended Improvements Before Reuse

If you plan to standardize this in multiple projects:

- Extract JS into dedicated static files instead of inline scripts.
- Create a reusable editor initializer module.
- Centralize API URLs and response parsing.
- Add typed contracts (or schema checks) for endpoint responses.
- Add reusable modal/tab components.
- Add integration tests for save/submit/import media flows.

---

## 10) Quick "Copy Blueprint"

If you only need the minimal reusable core:

- Copy `insight_form_new.html` structure.
- Keep these must-have behaviors:
  - blocks JSON parse/init,
  - `onChange` -> hidden field sync,
  - submit interception with awaited `editor.save()`,
  - cover preview update function,
  - media modal functions,
  - document upload-to-render flow.

Then adapt backend endpoints and model fields to your new project.

