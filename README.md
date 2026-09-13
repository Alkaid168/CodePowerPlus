# 码力加加（CodePowerPlus）

程序设计智能辅导系统。当前阶段先建设独立于学校 OJ 的最小原型。

## 本地运行

项目使用根目录下名为 `CodePowerPlus` 的虚拟环境。首次配置完成后，双击 `start_codepowerplus.bat` 即可启动；命令行也可运行 `CodePowerPlus\\Scripts\\python.exe -m uvicorn app.main:app --reload`。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs 查看 API。

## 配置 DeepSeek

复制 `.env.example` 为 `.env`，填写 `DEEPSEEK_API_KEY`。未配置密钥时，题目分析接口会返回 503，辅导接口仍可生成提示词供调试。

## 当前原型接口

- `POST /api/problems/analyze`：分析并保存题目
- `POST /api/submissions`：记录提交结果
- `GET /api/users/{user_id}/profile`：查看知识点掌握度
- `GET /api/users/{user_id}/recommendations`：获取推荐题目
- `POST /api/tutor/hint`：生成辅导提示或调用模型

## Docker 运行

```powershell
docker build -t codepowerplus .
docker run --rm -p 8000:8000 --env-file .env codepowerplus
```

首次体验可运行 `python scripts/seed_demo.py` 写入三道示例题目。
