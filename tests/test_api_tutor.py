"""辅导接口：未配置模型返回提示词预览，模型失败返回 503。"""
from dataclasses import replace

from fastapi.testclient import TestClient

from app.errors import ModelUnavailable
from app.main import create_app

BODY = {'problem': '给定数组求和', 'code': 'int main(){}', 'verdict': 'WA'}


def test_preview_without_model(client):
    response = client.post('/api/tutor/hint', json=BODY)
    assert response.status_code == 200
    body = response.json()
    assert body['message'] and 'int main(){}' in body['prompt']


def test_hint_with_model(settings, monkeypatch):
    monkeypatch.setattr('app.api.tutor.tutor_with_model', lambda *args, **kwargs: '先检查边界条件。')
    with TestClient(create_app(replace(settings, api_key='fake-key'))) as configured:
        body = configured.post('/api/tutor/hint', json=BODY).json()
    assert body == {'hint': '先检查边界条件。'}


def test_model_failure_returns_503(settings, monkeypatch):
    def boom(*args, **kwargs):
        raise ModelUnavailable('模型辅导暂不可用，请稍后重试')

    monkeypatch.setattr('app.api.tutor.tutor_with_model', boom)
    with TestClient(create_app(replace(settings, api_key='fake-key'))) as configured:
        response = configured.post('/api/tutor/hint', json=BODY)
    assert response.status_code == 503
    assert response.json()['code'] == 'model_unavailable'


def test_tutor_validates_payload(client):
    assert client.post('/api/tutor/hint', json={'problem': '', 'code': 'x', 'verdict': 'WA'}).status_code == 422
    assert client.post('/api/tutor/hint', json={'problem': 'x', 'code': 'y', 'verdict': 'OK'}).status_code == 422
