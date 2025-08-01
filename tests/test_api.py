import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from webapp import create_app
from webapp.config import TestConfig


def get_client():
    app = create_app(TestConfig)
    return app.test_client()


def test_get_card():
    client = get_client()
    res = client.get('/api/card')
    assert res.status_code == 200
    data = res.get_json()
    assert 'available' in data


def test_mark_card_invalid():
    client = get_client()
    res = client.post('/api/card/1', json={})
    assert res.status_code == 400


def test_grammar_list():
    client = get_client()
    res = client.get('/api/grammar')
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_update_grammar():
    client = get_client()
    res = client.post('/api/grammar/g001', json={'status': 'seen'})
    assert res.status_code == 200
    assert res.get_json()['status'] == 'ok'


def test_dashboard():
    client = get_client()
    res = client.get('/api/dashboard')
    assert res.status_code == 200
    data = res.get_json()
    assert 'total_cards' in data
    assert 'box_counts' in data
    assert 'grammar_status_counts' in data


def test_dashboard_counts_consistency():
    client = get_client()
    data = client.get('/api/dashboard').get_json()
    total_from_boxes = sum(data['box_counts'].values())
    assert total_from_boxes == data['total_cards']


def test_export_import():
    client = get_client()
    res = client.get('/api/export')
    assert res.status_code == 200
    exported = res.data.decode('utf-8')

    res = client.post('/api/import', data=exported)
    assert res.status_code == 200


def test_import_invalid_json():
    client = get_client()
    res = client.post('/api/import', data='not-json')
    assert res.status_code == 400

