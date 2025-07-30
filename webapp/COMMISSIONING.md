# Vox Web App Commissioning & Upgrade Tracker

This document outlines planned upgrades, refactoring, and enhancements for the Vox web application. Each section is organized by file/module. Use the checkboxes to track progress and add notes as you work.

---

## 1. `app.py` (Flask Backend)
- [x] Refactor to support environment-based config (dev/prod)
- [x] Add error handling and input validation to all endpoints
- [x] Modularize API routes (consider Blueprints)
- [ ] Add authentication (optional/future)
- [ ] Improve API documentation (docstrings, OpenAPI, etc.)
- [x] Ensure all data paths use `webapp/data/` and are robust to deployment location
- [x] Add logging for key actions and errors
- [x] Add unit tests for API endpoints


## 2. `static/app.js` (Frontend JS)
- [x] Refactor to use modern JS (ES6+ syntax, modular structure planned)
- [x] Improve error handling for fetch requests (try/catch, user feedback)
- [x] Add loading indicators and user feedback (loading spinner, error popups)
- [x] Refactor DOM manipulation for clarity and maintainability (querySelector, clear structure)
- [ ] Add client-side validation where appropriate (basic structure present, more needed)
- [ ] Add tests (Jest or similar, if feasible)

### New UI/UX Features
- [x] Display a centered large Chinese character with pinyin beneath
- [x] Input for user to guess the English translation
- [x] Add mode switch button (character→English or English→character)
- [x] Update logic to support both directions
- [x] Show feedback for correct/incorrect answers

## 3. `static/style.css` (Frontend CSS)
- [x] Redesign for a modern, visually appealing look (colors, spacing, fonts)
- [x] Center main quiz view (character/pinyin/guess input)
- [x] Make UI responsive for mobile/tablet
- [x] Add transitions/animations for interactivity
- [x] Improve accessibility (contrast, focus states, etc.)

## 4. `templates/index.html` (Frontend HTML)
- [x] Refactor structure for clarity and maintainability
- [ ] Add meta tags for SEO and mobile support
- [ ] Add favicon and app icon
- [x] Improve semantic HTML (use proper tags for tables, buttons, etc.)
- [x] Add accessibility features (aria-labels, roles)
- [x] Add main quiz view: centered character, pinyin, guess input, mode switch button

## 5. `data/` (Vocab & Grammar JSON)
- [x] Ensure `vocab_a1.json` and `grammar_a1.json` are present in `webapp/data/`
- [ ] Add data validation scripts/checks
- [ ] Add ability to update/extend data sets via admin UI or script

## 6. Backend Data Layer (DatabaseManager, etc.)
- [ ] Refactor to allow specifying data directory (not hardcoded)
- [ ] Add migration scripts for future schema changes
- [ ] Add backup/restore endpoints for webapp
- [ ] Add tests for data loading and saving

## 7. General/Project
- [ ] Add README badges (build, license, etc.)
- [ ] Add CONTRIBUTING.md and code style guide
- [ ] Add CI/CD pipeline (GitHub Actions, etc.)
- [ ] Add Dockerfile for easy deployment (optional)

---

**Instructions:**
- Check off items as you complete them.
- Add notes, links to PRs, or decisions as needed.
- Feel free to add new sections/files as the project evolves.

---

_Last updated: 2025-07-30_
