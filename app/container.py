"""依赖容器：把配置、数据库、知识树与仓储装配在一起。

接口层通过 ``get_container`` 取出它，因此测试可以给每个用例装配一套
「内存数据库 + 临时知识树」，不需要改任何全局变量。
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from app.config import Settings, load_settings
from app.db import Database
from app.knowledge import Taxonomy
from app.repositories import AnalysisRepository, ProblemRepository, ReviewRepository, SubmissionRepository


@dataclass
class Container:
    settings: Settings
    db: Database
    taxonomy: Taxonomy
    problems: ProblemRepository
    analyses: AnalysisRepository
    reviews: ReviewRepository
    submissions: SubmissionRepository

    @classmethod
    def build(cls, settings: Settings | None = None) -> 'Container':
        cfg = settings or load_settings()
        db = Database(cfg.db_path)
        return cls(
            settings=cfg,
            db=db,
            taxonomy=Taxonomy(cfg.taxonomy_path, cfg.schema_path),
            problems=ProblemRepository(db),
            analyses=AnalysisRepository(db),
            reviews=ReviewRepository(db),
            submissions=SubmissionRepository(db),
        )

    def close(self) -> None:
        self.db.close()


def get_container(request: Request) -> Container:
    return request.app.state.container
