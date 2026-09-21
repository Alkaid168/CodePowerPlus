"""题目接口：录入、列表、详情、模型分析与手工标注。"""
import pytest

from app.errors import InvalidInput


def manual_payload(version, **overrides):
    base = {
        'difficulty': 2,
        'confidence': 0.8,
        'primary_knowledge_ids': ['basic.prefix-sum'],
        'secondary_knowledge_ids': [],
        'evidence': {'basic.prefix-sum': '需要快速回答区间和'},
        'knowledge_confidence': {'basic.prefix-sum': 0.8},
        'taxonomy_version': version,
    }
    return base | overrides


def create_problem(client, title='两数之和'):
    response = client.post('/api/problems', json={'title': title, 'description': '给定数组。'})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_list_and_detail(client):
    problem = create_problem(client)
    assert problem['title'] == '两数之和'
    assert problem['analysis_status'] is None and problem['knowledge_ids'] == []

    listing = client.get('/api/problems').json()
    assert listing['total'] == 1 and listing['items'][0]['id'] == problem['id']
    assert client.get('/api/problems', params={'q': '不存在'}).json()['total'] == 0

    detail = client.get(f"/api/problems/{problem['id']}").json()
    assert detail['description'] == '给定数组。' and detail['analysis'] is None

    missing = client.get('/api/problems/9999')
    assert missing.status_code == 404 and missing.json()['code'] == 'not_found'


def test_manual_analysis_revisions_and_history(client, version):
    problem = create_problem(client)
    first = client.post(f"/api/problems/{problem['id']}/analyses", json=manual_payload(version))
    assert first.status_code == 201, first.text
    first_analysis = first.json()['analysis']
    assert first_analysis['review_status'] == 'pending' and first_analysis['origin'] == 'manual'
    assert first_analysis['tags'] == ['前缀和']

    second = client.post(f"/api/problems/{problem['id']}/analyses",
                         json=manual_payload(version, primary_knowledge_ids=['basic.binary'],
                                             evidence={'basic.binary': '需要在有序序列上二分'},
                                             knowledge_confidence={'basic.binary': 0.8}))
    assert second.status_code == 201
    second_analysis = second.json()['analysis']
    assert second_analysis['analysis_id'] > first_analysis['analysis_id']

    detail = client.get(f"/api/problems/{problem['id']}").json()
    assert detail['analysis']['analysis_id'] == second_analysis['analysis_id']
    assert detail['knowledge_ids'] == ['basic.binary']

    history = client.get(f"/api/problems/{problem['id']}/analyses").json()['items']
    assert [item['analysis_id'] for item in history] == [second_analysis['analysis_id'],
                                                         first_analysis['analysis_id']]


@pytest.mark.parametrize('change', [
    {'primary_knowledge_ids': [], 'evidence': {}, 'knowledge_confidence': {}},
    {'primary_knowledge_ids': ['invented']},
    {'primary_knowledge_ids': ['math']},
    {'evidence': {}},
    {'knowledge_confidence': {}},
    {'taxonomy_version': '2020.01.1'},
])
def test_invalid_manual_analysis_is_rejected(client, version, change):
    problem = create_problem(client)
    response = client.post(f"/api/problems/{problem['id']}/analyses", json=manual_payload(version, **change))
    assert response.status_code == 422, response.text
    assert response.json()['code'] in {'invalid_input', 'invalid_request'}
    assert client.get(f"/api/problems/{problem['id']}").json()['analysis'] is None


def test_manual_analysis_requires_version(client):
    problem = create_problem(client)
    payload = manual_payload('')
    response = client.post(f"/api/problems/{problem['id']}/analyses", json=payload)
    assert response.status_code == 422


def test_model_analysis_is_persisted(client, monkeypatch, version):
    from app.api import problems as problems_api
    from app.schemas import AnalysisPayload

    def fake(description, taxonomy, settings):
        return AnalysisPayload(difficulty=3, confidence=0.9, primary_knowledge_ids=['string.kmp'],
                               evidence={'string.kmp': '需要 KMP'}, knowledge_confidence={'string.kmp': 0.9},
                               taxonomy_version=taxonomy.version, model_name=settings.model)

    monkeypatch.setattr(problems_api, 'analyze_with_model', fake)
    response = client.post('/api/problems/analyze', json={'title': '模式匹配', 'description': '统计模式串出现次数'})
    assert response.status_code == 201, response.text
    body = response.json()
    assert body['problem']['title'] == '模式匹配'
    assert body['analysis']['origin'] == 'model' and body['analysis']['review_status'] == 'pending'
    assert body['analysis']['model_name']


def test_model_invalid_output_is_rejected(client, monkeypatch):
    from app.api import problems as problems_api

    def boom(*args, **kwargs):
        raise InvalidInput('模型连续返回不符合知识标注规范的内容')

    monkeypatch.setattr(problems_api, 'analyze_with_model', boom)
    response = client.post('/api/problems/analyze', json={'title': 'x', 'description': 'd'})
    assert response.status_code == 422
    assert response.json()['code'] == 'invalid_input'


def test_model_unavailable_returns_503(client, monkeypatch):
    from app.api import problems as problems_api
    from app.errors import ModelUnavailable

    def boom(*args, **kwargs):
        raise ModelUnavailable('尚未配置模型密钥')

    monkeypatch.setattr(problems_api, 'analyze_with_model', boom)
    response = client.post('/api/problems/analyze', json={'title': 'x', 'description': 'd'})
    assert response.status_code == 503
    assert response.json()['code'] == 'model_unavailable'
