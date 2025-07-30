from flask import Blueprint, current_app, jsonify, request
from ..database import DatabaseManager, Card, GrammarPoint
from typing import Optional
import logging
import json

api_bp = Blueprint('api', __name__)

# Database instance will be attached when blueprint is registered
api_db: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    if api_db is None:
        raise RuntimeError('Database not initialized')
    return api_db


@api_bp.route('/card')
def get_card():
    """Return the next vocab card to review."""
    try:
        card = get_db().get_card_to_review()
    except Exception:
        current_app.logger.exception('Failed to retrieve card')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Retrieved card: %s', card.id if card else 'none')

    if not card:
        return jsonify({'available': False})

    return jsonify({'available': True, 'card': {
        'id': card.id,
        'hanzi': card.hanzi,
        'pinyin': card.pinyin,
        'english': card.english,
    }})


@api_bp.route('/card/<card_id>', methods=['POST'])
def mark_card(card_id):
    """Update progress for a vocab card."""
    data = request.get_json(silent=True) or {}
    correct = data.get('correct')
    if correct is None or not isinstance(correct, bool):
        return jsonify({'error': 'invalid input'}), 400
    try:
        get_db().update_card_progress(card_id, correct)
    except Exception:
        current_app.logger.exception('Failed to update card')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Updated card %s with correct=%s', card_id, correct)
    return jsonify({'status': 'ok'})


@api_bp.route('/grammar')
def grammar_list():
    """Return all grammar points."""
    try:
        points = get_db().get_all_grammar_points()
    except Exception:
        current_app.logger.exception('Failed to load grammar list')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Returned %d grammar points', len(points))

    return jsonify([{
        'id': p.id,
        'structure': p.structure,
        'pattern': p.pattern,
        'explanation': p.explanation,
        'status': p.status,
    } for p in points])


@api_bp.route('/grammar/<grammar_id>', methods=['POST'])
def update_grammar(grammar_id):
    """Update grammar status."""
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in {'unseen', 'seen', 'practiced', 'mastered'}:
        return jsonify({'error': 'invalid input'}), 400
    try:
        get_db().update_grammar_status(grammar_id, status)
    except Exception:
        current_app.logger.exception('Failed to update grammar')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Updated grammar %s to status %s', grammar_id, status)
    return jsonify({'status': 'ok'})


@api_bp.route('/dashboard')
def dashboard():
    """Return dashboard statistics."""
    try:
        stats = get_db().get_dashboard_stats()
    except Exception:
        current_app.logger.exception('Failed to get dashboard stats')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Fetched dashboard stats')
    return jsonify(stats)


@api_bp.route('/export')
def export_progress():
    """Export current progress as JSON string."""
    try:
        json_data = get_db().export_progress_to_json()
    except Exception:
        current_app.logger.exception('Failed to export progress')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Exported progress JSON')
    return current_app.response_class(json_data, mimetype='application/json')


@api_bp.route('/import', methods=['POST'])
def import_progress():
    """Import progress from JSON string."""
    json_data = request.data.decode('utf-8')
    try:
        get_db().import_progress_from_json(json_data)
    except json.JSONDecodeError:
        return jsonify({'error': 'invalid json'}), 400
    except Exception:
        current_app.logger.exception('Failed to import progress')
        return jsonify({'error': 'internal'}), 500
    current_app.logger.info('Imported progress JSON')
    return jsonify({'status': 'ok'})

