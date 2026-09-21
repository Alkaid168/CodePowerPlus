"""人工审核：把「待审核分析」变成「批准/驳回」，并留下不可丢的审计记录。

两条关键规则：
- 乐观锁：请求必须带上它看到的 analysis_id，服务端在事务里重新读一次，
  对不上就返回 409，避免两个审核人互相覆盖。
- 纠正即新版本：审核通过时允许顺带修改标签，但修改会产生一条新的分析记录，
  原来的版本仍然留着，审计里能看到 original → new 的对应关系。
"""
from __future__ import annotations

from app.errors import Conflict, InvalidInput, NotFound
from app.repositories import AnalysisRepository, ProblemRepository, ReviewRepository
from app.schemas import AnalysisPayload, ReviewRequest
from app.services.analysis import validate


def apply_review(*, db, problems: ProblemRepository, analyses: AnalysisRepository, reviews: ReviewRepository,
                 taxonomy, problem_id: int, request: ReviewRequest) -> tuple[dict, dict]:
    problem = problems.get(problem_id)
    if problem is None:
        raise NotFound('题目不存在')
    with db.transaction():
        current = analyses.latest(problem_id)
        if (current is None or current['analysis_id'] != request.expected_analysis_id
                or current['review_status'] != 'pending'):
            raise Conflict('分析已被修改或审核，请刷新后重试')
        correction: AnalysisPayload | None = None
        if request.correction is not None:
            if request.action != 'approve':
                raise InvalidInput('驳回时不能同时提交纠正内容')
            correction = validate(request.correction, taxonomy, model_name='manual',
                                  require_current_version=True)
        elif request.action == 'approve':
            if current.get('taxonomy_version') != taxonomy.version:
                raise InvalidInput('旧版分析需要重新标注后才能批准')
            validate(AnalysisPayload.model_validate(current), taxonomy,
                     model_name=current.get('model_name') or 'manual')
        target_id = current['analysis_id']
        if correction is not None:
            target_id = analyses.add(problem_id, correction.model_dump(), origin='manual',
                                     status='pending', taxonomy_version=taxonomy.version)['analysis_id']
        reviews.add(problem_id, request.expected_analysis_id, target_id, request.action,
                    request.reviewer, request.comment)
    return problem, analyses.get(target_id)
