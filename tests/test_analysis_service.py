"""分析服务：标签规则、模型输出解析、模型失败时的降级。"""
from dataclasses import replace

import pytest

from app.config import load_settings
from app.errors import InvalidInput, ModelUnavailable
from app.knowledge import Taxonomy
from app.schemas import AnalysisPayload
from app.services.analysis import analyze_with_model, knowledge_ids, parse_json_response, validate


@pytest.fixture()
def taxonomy():
    return Taxonomy()


def payload(**overrides):
    base = {
        'title': 'x',
        'difficulty': 2,
        'confidence': 0.8,
        'primary_knowledge_ids': ['basic.prefix-sum'],
        'secondary_knowledge_ids': [],
        'evidence': {'basic.prefix-sum': '需要前缀和'},
        'knowledge_confidence': {'basic.prefix-sum': 0.8},
    }
    return AnalysisPayload.model_validate(base | overrides)


def test_validate_stamps_server_fields(taxonomy):
    result = validate(payload(), taxonomy, model_name='manual')
    assert result.taxonomy_version == taxonomy.version
    assert result.model_name == 'manual'
    assert result.prompt_version == 'manual-v1'
    assert result.tags == ['前缀和']
    assert knowledge_ids(result) == ['basic.prefix-sum']


def test_manual_analysis_must_declare_current_version(taxonomy):
    with pytest.raises(InvalidInput):
        validate(payload(), taxonomy, model_name='manual', require_current_version=True)
    with pytest.raises(InvalidInput):
        validate(payload(taxonomy_version='2020.01.1'), taxonomy, model_name='manual')
    ok = validate(payload(taxonomy_version=taxonomy.version), taxonomy, model_name='manual',
                  require_current_version=True)
    assert ok.taxonomy_version == taxonomy.version


def test_validate_rejects_unknown_tag_missing_evidence_and_bad_confidence(taxonomy):
    with pytest.raises(InvalidInput):
        validate(payload(primary_knowledge_ids=['nope'], evidence={'nope': 'x'},
                         knowledge_confidence={'nope': 0.5}), taxonomy, model_name='manual')
    with pytest.raises(InvalidInput):
        validate(payload(evidence={}, knowledge_confidence={}), taxonomy, model_name='manual')
    with pytest.raises(InvalidInput):
        validate(payload(knowledge_confidence={'basic.prefix-sum': 1.5}), taxonomy, model_name='manual')
    with pytest.raises(InvalidInput):
        validate(payload(evidence={'basic.prefix-sum': '   '}), taxonomy, model_name='manual')


def test_parse_json_response_strips_markdown_fences():
    raw = ('```json\n'
           '{"difficulty": 3, "confidence": 0.5, "primary_knowledge_ids": ["basic.prefix-sum"],'
           ' "evidence": {"basic.prefix-sum": "前缀和"}, "knowledge_confidence": {"basic.prefix-sum": 0.5}}\n'
           '```')
    assert parse_json_response(raw).difficulty == 3
    with pytest.raises(InvalidInput):
        parse_json_response('不是 JSON')


def test_model_without_key_is_unavailable(taxonomy):
    with pytest.raises(ModelUnavailable):
        analyze_with_model('题面', taxonomy, replace(load_settings(), api_key=''))


def test_model_client_failure_becomes_model_unavailable(taxonomy, monkeypatch):
    import openai

    class Boom:
        def __init__(self, **kwargs):
            raise RuntimeError('proxy down')

    monkeypatch.setattr(openai, 'OpenAI', Boom)
    with pytest.raises(ModelUnavailable):
        analyze_with_model('题面', taxonomy, replace(load_settings(), api_key='fake-key'))
