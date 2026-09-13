# 码力加加（CodePowerPlus）

程序设计智能辅导系统。当前阶段先建设独立于学校 OJ 的最小原型。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs 查看 API。
