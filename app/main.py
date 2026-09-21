"""应用组装：创建 FastAPI 实例、挂载接口与静态前端。

所有业务依赖由 ``Container`` 提供，接口层只通过 ``get_container`` 取用，
因此测试可以给每个用例装配内存数据库，而不必修改模块全局变量。
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import Settings
from app.container import Container
from app.errors import install_error_handlers
from app.schemas import HealthOut


def create_app(settings: Settings | None = None) -> FastAPI:
    container = Container.build(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        container.close()

    app = FastAPI(title='码力加加智能辅导系统', version=container.settings.app_version,
                  description='面向算法竞赛训练的题目分析、能力画像、代码辅导与推荐原型。',
                  lifespan=lifespan)
    app.state.container = container
    install_error_handlers(app)
    app.include_router(api_router)

    @app.get('/health', response_model=HealthOut, tags=['meta'])
    def health():
        return {'status': 'ok', 'message': '码力加加服务运行正常',
                'version': container.settings.app_version,
                'taxonomy_version': container.taxonomy.version,
                'model_configured': container.settings.model_configured,
                'mode': 'local-single-user'}

    @app.get('/', include_in_schema=False)
    def homepage():
        return FileResponse(container.settings.web_dir / 'index.html')

    app.mount('/static', StaticFiles(directory=container.settings.web_dir), name='static')
    return app


app = create_app()
