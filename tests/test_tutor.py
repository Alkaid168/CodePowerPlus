"""辅导提示：分级提示词与“未配置模型”时的降级。"""
from dataclasses import replace

import pytest

from app.config import load_settings
from app.errors import ModelUnavailable
from app.services.tutor import build_hint_prompt, tutor_with_model


def test_prompt_asks_for_graduated_hints():
    prompt = build_hint_prompt('两数之和', 'int main(){}', 'WA')
    assert '评测结果：WA' in prompt
    assert '不要直接给出完整正确代码' in prompt
    assert '第一层' in prompt and '第三层' in prompt


def test_timeout_hint_mentions_complexity():
    assert '复杂度' in build_hint_prompt('x', 'code', 'TLE')


def test_accepted_submission_gets_congratulation():
    assert '已经通过' in build_hint_prompt('x', 'code', 'AC')


def test_model_requires_configuration():
    with pytest.raises(ModelUnavailable):
        tutor_with_model('p', 'c', 'WA', replace(load_settings(), api_key=''))
