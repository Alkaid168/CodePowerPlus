"""题目与分析接口：录入、模型分析、手工标注、版本历史。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api import problem_detail, problem_summary, require_problem
from app.container import Container, get_container
from app.schemas import (AnalysisHistoryOut, AnalysisPayload, AnalyzeRequest, ProblemCreate, ProblemDetailOut,
                         ProblemListOut, ProblemSummaryOut, ProblemWithAnalysisOut)
from app.services.analysis import analyze_with_model, validate

router = APIRouter(prefix='/api/problems', tags=['problems'])


@router.post('', response_model=ProblemSummaryOut, status_code=201)
def create_problem(payload: ProblemCreate, container: Container = Depends(get_container)):
    problem = container.problems.create(payload.title, payload.description, payload.source)
    return problem_summary(problem, None)


@router.post('/analyze', response_model=ProblemWithAnalysisOut, status_code=201)
def analyze_new_problem(payload: AnalyzeRequest, container: Container = Depends(get_container)):
    analysis = analyze_with_model(payload.description, container.taxonomy, container.settings)
    title = payload.title or analysis.title or '未命名题目'
    problem = container.problems.create(title, payload.description, payload.source)
    saved = container.analyses.add(problem['id'], {**analysis.model_dump(), 'title': title}, origin='model',
                                   status='pending', taxonomy_version=container.taxonomy.version)
    return {'problem': problem_summary(problem, saved), 'analysis': saved}


@router.get('', response_model=ProblemListOut)
def list_problems(q: str = '', limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
                  container: Container = Depends(get_container)):
    problems, total = container.problems.list(q, limit, offset)
    latest = container.analyses.latest_by_problem([problem['id'] for problem in problems])
    return {'items': [problem_summary(problem, latest.get(problem['id'])) for problem in problems],
            'total': total, 'offset': offset, 'limit': limit}


@router.get('/{problem_id}', response_model=ProblemDetailOut)
def get_problem(problem_id: int, container: Container = Depends(get_container)):
    problem = require_problem(container, problem_id)
    return problem_detail(problem, container.analyses.latest(problem_id))


@router.post('/{problem_id}/analyze', response_model=ProblemWithAnalysisOut, status_code=201)
def analyze_existing_problem(problem_id: int, container: Container = Depends(get_container)):
    problem = require_problem(container, problem_id)
    analysis = analyze_with_model(problem['description'], container.taxonomy, container.settings)
    saved = container.analyses.add(problem_id, {**analysis.model_dump(), 'title': problem['title']},
                                   origin='model', status='pending', taxonomy_version=container.taxonomy.version)
    return {'problem': problem_summary(problem, saved), 'analysis': saved}


@router.post('/{problem_id}/analyses', response_model=ProblemWithAnalysisOut, status_code=201)
def manual_analysis(problem_id: int, payload: AnalysisPayload, container: Container = Depends(get_container)):
    problem = require_problem(container, problem_id)
    analysis = validate(payload, container.taxonomy, model_name='manual', require_current_version=True)
    saved = container.analyses.add(problem_id, analysis.model_dump(), origin='manual', status='pending',
                                   taxonomy_version=container.taxonomy.version)
    return {'problem': problem_summary(problem, saved), 'analysis': saved}


@router.get('/{problem_id}/analyses', response_model=AnalysisHistoryOut)
def analysis_history(problem_id: int, container: Container = Depends(get_container)):
    require_problem(container, problem_id)
    return {'items': container.analyses.history(problem_id)}
