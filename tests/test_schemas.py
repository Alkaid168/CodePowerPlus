"""请求契约：多余字段一律拒绝，取值范围由 Pydantic 兜住。"""
import pytest
from pydantic import ValidationError

from app.schemas import AnalysisPayload, ProblemCreate, ReviewRequest, SubmissionCreate


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        SubmissionCreate(user_id='u1', problem_id=1, verdict='AC', tags=['forged'])
    with pytest.raises(ValidationError):
        ProblemCreate(title='t', description='d', owner='me')
    with pytest.raises(ValidationError):
        ReviewRequest(action='approve', reviewer='r', expected_analysis_id=1, extra='x')


def test_value_ranges_are_validated():
    with pytest.raises(ValidationError):
        SubmissionCreate(user_id='u1', problem_id=1, verdict='OK')
    with pytest.raises(ValidationError):
        SubmissionCreate(user_id='', problem_id=1, verdict='AC')
    with pytest.raises(ValidationError):
        AnalysisPayload(difficulty=6, confidence=0.5)
    with pytest.raises(ValidationError):
        AnalysisPayload(difficulty=2, confidence=1.5)
    valid = AnalysisPayload(difficulty=2, confidence=0.5,
                            primary_knowledge_ids=['basic.prefix-sum'],
                            evidence={'basic.prefix-sum': '前缀和'},
                            knowledge_confidence={'basic.prefix-sum': 0.5})
    assert valid.taxonomy_version == ''
