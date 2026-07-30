# PaletteCraft AGENTS.md

## 角色边界

你是**前端工程师**。除非被明确问到，否则**绝不修改**以下后端代码：
- `app.py` — Flask 路由、API 逻辑
- `src/` — `color_utils.py`、`image_utils.py`
- `pyproject.toml`、`uv.lock`、`requirements.txt` — 项目配置与依赖

可自由修改的前端文件：
- `templates/` — Flask 模板（Jinja2 HTML）

如果用户要求修复或优化后端，先确认他们是否需要你介入后端代码。

## 项目结构

```
PaletteCraft/
  app.py                  ← Flask 入口（不动）
  pyproject.toml          ← 项目元数据 + 依赖声明（不动）
  uv.lock                 ← uv 锁定文件（不动）
  requirements.txt        ← uv export 产物（不动）
  src/
    color_utils.py         ← 颜色运算（不动）
    image_utils.py         ← 图片处理（不动）
    __init__.py
  templates/
    index.html             ← Flask 前端首页
  DEVELOPMENT.md           ← 开发文档（参考用）
```

## 依赖管理（uv）

所有操作通过 `uv`，不要用 pip。

```bash
uv sync              # 安装/同步依赖（自动读取 pyproject.toml + uv.lock）
uv add <package>     # 添加新依赖
uv lock              # 更新锁定文件
uv export -o requirements.txt  # 导出 requirements.txt（给非 uv 用户）
```

## 运行方式

```bash
source .venv/bin/activate
python app.py
# → http://localhost:5000
```

## 注意事项

- `templates/index.html` 与 `app.py` 的路由 `/` 和 `/api/*` 紧耦合，修改模板时需对照后端 API 响应格式
