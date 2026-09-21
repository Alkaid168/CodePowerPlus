"""审核接口：待审队列、提交审核、查看审计记录。"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends

from app.api import problem_detail, problem_summary, problems_with_analysis, require_problem
from app.container import Container, get_container
from app.schemas import ReviewListOut, ReviewQueueOut, ReviewRequest, ReviewResultOut
from app.services.review import apply_review

router = APIRouter(tags=['reviews'])


@router.get('/api/reviews', response_model=ReviewQueueOut)
def review_queue(status: Literal['pending', 'approved', 'rejected', 'legacy'] = 'pending',
                 container: Container = Depends(get_container)):
    items = []
    for problem in problems_with_analysis(container):
        analysis = problem['analysis']
        if analysis and analysis['review_status'] == status:
            items.append(problem_detail(problem, analysis))
    return {'items': items}


@router.post('/api/problems/{problem_id}/review', response_model=ReviewResultOut)
def review_problem(problem_id: int, payload: ReviewRequest,
                   container: Container = Depends(get_container)):
    problem, analysis = apply_review(db=container.db, problems=container.problems,
                                     analyses=container.analyses, reviews=container.reviews,
                                     taxonomy=container.taxonomy, problem_id=problem_id, request=payload)
    return {'problem': problem_summary(problem, analysis), 'analysis': analysis}


@router.get('/api/problems/{problem_id}/reviews', response_model=ReviewListOut)
def review_history(problem_id: int, container: Container = Depends(get_container)):
    require_problem(container, problem_id)
    return {'items': container.reviews.list_for_problem(problem_id)}
