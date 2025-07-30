# Vox Web App Commissioning & Upgrade Tracker

This document outlines planned upgrades, refactoring, and enhancements for the Vox web application. Each section is organized by file/module. Use the checkboxes to track progress and add notes as you work.

---

## 1. `app.py` (Flask Backend)
- [x] Refactor to support environment-based config (dev/prod)
- [ ] Add error handling and input validation to all endpoints
- [ ] Modularize API routes (consider Blueprints)
- [ ] Add authentication (optional/future)
- [ ] Improve API documentation (docstrings, OpenAPI, etc.)
- [ ] Ensure all data paths use `webapp/data/` and are robust to deployment location
- [ ] Add logging for key actions and errors
- [ ] Add unit tests for API endpoints

## 2. `static/app.js` (Frontend JS)
- [ ] Refactor to use modern JS (ES6+, modules if possible)
- [ ] Improve error handling for fetch requests
- [ ] Add loading indicators and user feedback
- [ ] Refactor DOM manipulation for clarity and maintainability
- [ ] Add client-side validation where appropriate
- [ ] Add tests (Jest or similar, if feasible)

### New UI/UX Features
- [ ] Display a centered large Chinese character with pinyin beneath
- [ ] Input for user to guess the English translation
- [ ] Add mode switch button (character→English or English→character)
- [ ] Update logic to support both directions
- [ ] Show feedback for correct/incorrect answers

## 3. `static/style.css` (Frontend CSS)
- [ ] Redesign for a modern, visually appealing look (colors, spacing, fonts)
- [ ] Center main quiz view (character/pinyin/guess input)
- [ ] Make UI responsive for mobile/tablet
- [ ] Add transitions/animations for interactivity
- [ ] Improve accessibility (contrast, focus states, etc.)

## 4. `templates/index.html` (Frontend HTML)
- [ ] Refactor structure for clarity and maintainability
- [ ] Add meta tags for SEO and mobile support
- [ ] Add favicon and app icon
- [ ] Improve semantic HTML (use proper tags for tables, buttons, etc.)
- [ ] Add accessibility features (aria-labels, roles)
- [ ] Add main quiz view: centered character, pinyin, guess input, mode switch button

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
