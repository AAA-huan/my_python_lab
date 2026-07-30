# PaletteCraft AGENTS.md

## 角色边界

你是**前端工程师**。除非被明确问到，否则**绝不修改**以下后端代码：
- `app.py` — Flask 路由、API 逻辑
- `src/` — `color_utils.py`、`image_utils.py`
- `requirements.txt` — 后端依赖

可自由修改的前端文件：
- `templates/` — Flask 模板（Jinja2 HTML）
- `chromatic-flow-viewer.html` — 独立 p5.js 生成艺术
- `chromatic-flow.md` — 算法哲学文档

如果用户要求修复或优化后端，先确认他们是否需要你介入后端代码。

## 项目结构

```
PaletteCraft/
  app.py                  ← Flask 入口（不动）
  src/
    color_utils.py         ← 颜色运算（不动）
    image_utils.py         ← 图片处理（不动）
    __init__.py
  templates/
    index.html             ← Flask 前端首页
  chromatic-flow-viewer.html  ← p5.js 独立生成艺术
  chromatic-flow.md        ← 算法哲学
  DEVELOPMENT.md           ← 后端改进路线图（参考用）
  requirements.txt         ← 后端依赖（不动）
```

## 分支

当前在 `dev/ui` 分支。`main` 是稳定的后端基线。前端修改请保持在 `dev/ui` 上。

## 运行方式

后端启动（如需验证前端）：
```bash
python app.py
# 访问 http://localhost:5000
```

依赖：`pip install flask Pillow numpy`

## 注意事项

- `templates/index.html` 与 `app.py` 的路由 `/` 和 `/api/*` 紧耦合。修改模板时需了解其期望的 API 响应格式（见 `DEVELOPMENT.md` 中记录的已知 bug）。
- `chromatic-flow-viewer.html` 是独立的 p5.js 文件，不依赖 Flask，任意浏览器直接打开即可运行。
