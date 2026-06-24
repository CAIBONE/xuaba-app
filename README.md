# 学吧 - AI 智能学习助手

完整的 AI 驱动学习助手应用，支持知识图谱生成、教材自动生成、智能测验、学习进度跟踪和数据分析。

## 技术栈

- **后端**: Python 3.11+ / FastAPI / LangChain
- **数据库**: PostgreSQL 16 / Redis 7
- **前端**: 微信小程序（已完成）
- **管理后台**: Web 界面（Chart.js）
- **部署**: Docker

## 核心功能

### 学习管理
- 📚 项目管理 - 创建学习项目，设定目标和截止日期
- 🌳 知识图谱生成 - AI 自动生成知识点图谱（支持 2-track 目标梳理）
- 📖 教材自动生成 - 为每个知识点生成详细教材（Markdown 自动转 HTML）
- 📝 智能测验 - 自动生成选择题和简答题
- ✅ 学习进度跟踪 - 节点状态实时更新（pending/in_progress/completed）

### 数据分析
- 📊 学习进度报表 - 完成率、学时统计
- 🔥 打卡热力图 - 学习活跃度可视化
- 📉 遗忘曲线 - 基于艾宾浩斯遗忘曲线的复习提醒
- 🎯 薄弱知识点 - 自动识别需要加强的知识点

### 管理后台
- 👥 用户管理 - 用户列表、详情、统计
- 📁 项目管理 - 项目列表、知识图谱查看
- 📈 仪表板 - 用户数、项目数、知识点数等统计
- ⚙️ 系统配置 - LLM 配置、系统信息

### 智能特性
- 🤖 2-track 目标梳理 - 考试型/技能型不同策略
- 🔍 6 步知识图谱验证 - 确保图谱质量
- 🔄 批量内容生成 - 一次生成多个节点教材
- 🔐 真实微信登录 - code2Session 认证
- ⚡ 429 限流自动重试 - 每 5 分钟重试，最多 10 次

## 架构

```
微信小程序 ←→ API Gateway ←→ Main Agent Service ←→ LLM
                                  ↓ HTTP 审计请求
                            Audit Agent Service ←→ LLM
                                  ↓
                            PostgreSQL + Redis
```

## 核心数据流

```
启动 → 建档 → 生成知识图谱 → 生成学习计划 → 生成推送教材 → 用户学习
  → 生成测验 → 用户测验 → 更新掌握度 → 更新档案 → LOOP
```

## 快速开始

### 1. 启动数据库

```bash
docker-compose up -d
```

### 2. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际配置
```

### 4. 初始化数据库

```bash
alembic upgrade head
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。
访问 http://localhost:8000/admin 进入管理后台。

## 使用示例

### 创建学习项目
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "中级经济师",
    "goal_description": "零基础通过2026年考试",
    "goal_type": "exam",
    "deadline": "2026-11-30"
  }'
```

### 生成知识图谱
```bash
curl -X POST http://localhost:8000/api/projects/1/generate-tree \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 批量生成教材
```bash
curl -X POST http://localhost:8000/api/contents/batch-generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "node_ids": [1, 2, 3],
    "content_type": "lesson"
  }'
```

## API 端点

### 认证
- `POST /api/auth/login` - 微信登录
- `PUT /api/auth/profile` - 更新用户资料
- `GET /api/auth/me` - 获取当前用户

### 项目管理
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目
- `POST /api/projects/{id}/generate-tree` - 生成知识图谱
- `POST /api/projects/{id}/refine-goal` - 目标梳理（2-track）

### 知识节点
- `GET /api/nodes/project/{id}` - 获取项目节点
- `PUT /api/nodes/{id}` - 更新节点状态
- `GET /api/nodes/project/{id}/tree` - 获取知识图谱

### 教材生成
- `POST /api/contents/generate` - 生成单个教材
- `POST /api/contents/batch-generate` - 批量生成教材

### 测验
- `POST /api/quizzes/generate` - 生成测验
- `POST /api/quizzes/{id}/submit` - 提交答案

### 报表
- `GET /api/reports/progress/{project_id}` - 学习进度
- `GET /api/reports/heatmap` - 打卡热力图
- `GET /api/reports/forgetting/{project_id}` - 遗忘曲线
- `GET /api/reports/weak-nodes/{project_id}` - 薄弱知识点

### 管理后台
- `GET /api/admin/dashboard` - 仪表板统计
- `GET /api/admin/users` - 用户列表
- `GET /api/admin/projects` - 项目列表
- `GET /api/admin/system` - 系统信息

## 数据库表结构

### 主表
- `users` - 用户
- `projects` - 学习项目（含目标、知识图谱元信息）
- `nodes` - 知识节点
- `contents` - 教材

### 业务表
- `schedules` - 学习计划（按节点排程）
- `quizzes` - 测验
- `push_records` - 推送记录
- `mastery_history` - 掌握度历史
- `study_logs` - 学习日志

### 支表
- `audit_records` - 审计记录
- `conversations` - 对话历史
- `notes` - 笔记和划线

## 报表功能

- 学习进度
- 知识点掌握度变化
- 打卡热力图
- 遗忘曲线
- 已学习但欠掌握知识点

## 开发计划

- [x] Phase 1: 项目骨架 + 数据库
- [x] Phase 2: Agent 逻辑 + 知识图谱/教材/测验生成
- [x] Phase 3: 微信小程序（完整功能）
- [x] Phase 4: 管理后台 + 报表系统 + 状态跟踪
- [ ] 后续：每日学习计划 + 推送提醒（Issue 10）
- [ ] 后续：UI/UX 美化（Issue 11）

## License

MIT
