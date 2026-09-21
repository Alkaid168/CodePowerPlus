"""辅导接口：有模型时给出提示，没有模型时返回将要发送的提示词预览。"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.container import Container, get_container
from app.schemas import HintOut, HintPreviewOut, TutorRequest
from app.services.tutor import build_hint_prompt, tutor_with_model

router = APIRouter(prefix='/api/tutor', tags=['tutor'])


@router.post('/hint', response_model=HintOut | HintPreviewOut)
def tutor_hint(payload: TutorRequest, container: Container = Depends(get_container)):
    if container.settings.model_configured:
        return HintOut(hint=tutor_with_model(payload.problem, payload.code, payload.verdict,
                                             container.settings)).model_dump()
    return HintPreviewOut(prompt=build_hint_prompt(payload.problem, payload.code, payload.verdict),
                          message='尚未配置模型，以下为辅导请求预览。').model_dump()
