# 学吧 - AI 智能学习助手

独立的 AI 学习助手应用，脱离飞书和 OpenClaw 依赖。

## 技术栈

- **后端**: Python 3.11+ / FastAPI / LangChain
- **数据库**: PostgreSQL 16 / Redis 7
- **前端**: 微信小程序（开发中）
- **部署**: Docker

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

## 报表功能

- 学习进度
- 知识点掌握度变化
- 打卡热力图
- 遗忘曲线
- 已学习但欠掌握知识点

## 开发计划

- [x] Phase 1: 项目骨架 + 数据库
- [ ] Phase 2: Agent 逻辑（Main + Audit）
- [ ] Phase 3: 微信小程序

## License

MIT
