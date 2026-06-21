"""审计工具"""
from typing import Type, Literal
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.agents.llm import audit_llm


AuditType = Literal["knowledge_tree", "content", "quiz"]


class AuditCheck(BaseModel):
    """审计检查项"""
    name: str = Field(description="检查项名称")
    severity: str = Field(description="严重程度：hard/soft")
    passed: bool = Field(description="是否通过")
    details: str = Field(default="", description="详细说明")
    fix_action: str = Field(default="", description="修复建议")


class AuditInput(BaseModel):
    """审计输入"""
    audit_type: AuditType = Field(description="审计类型")
    artifact: dict = Field(description="待审计的生成物")
    context: dict = Field(default_factory=dict, description="上下文信息")


class AuditOutput(BaseModel):
    """审计输出"""
    verdict: str = Field(description="结论：passed/passed_with_notes/not_passed")
    checks: list[AuditCheck] = Field(description="检查项结果")
    failed_hard: int = Field(description="硬指标失败数")
    failed_soft: int = Field(description="软指标失败数")
    summary: str = Field(description="审计总结")


KNOWLEDGE_TREE_AUDIT_PROMPT = """你是学习质量审计专家，负责独立审查知识图谱的质量。

请审查以下知识图谱：

**科目**：{subject}
**学习目标**：{goal}
**知识节点**：
{nodes}

审查标准：
1. **结构完整性**（hard）：节点是否有合理的层次结构
2. **依赖合理性**（hard）：prerequisites 是否形成合理的依赖关系
3. **无循环依赖**（hard）：检查是否存在循环依赖
4. **时间合理性**（soft）：各节点时间预估是否合理
5. **覆盖完整性**（soft）：是否覆盖了学习目标的所有关键知识
6. **命名清晰度**（soft）：节点标题是否清晰易懂

请输出 JSON 格式：
{{
  "verdict": "passed/passed_with_notes/not_passed",
  "checks": [
    {{"name": "检查项", "severity": "hard/soft", "passed": true/false, "details": "说明", "fix_action": "修复建议"}}
  ],
  "failed_hard": 0,
  "failed_soft": 0,
  "summary": "审计总结"
}}
"""

CONTENT_AUDIT_PROMPT = """你是学习质量审计专家，负责独立审查学习教材的质量。

请审查以下教材：

**知识点**：{node_title}
**教材标题**：{title}
**教材内容**：
{content}

审查标准：
1. **字数达标**（hard）：内容字数是否符合预计阅读时间（250-300字/分钟）
2. **结构完整**（hard）：是否有清晰的章节结构
3. **知识准确**（hard）：内容是否准确无明显错误
4. **难度匹配**（soft）：内容难度是否符合设定
5. **实例充分**（soft）：是否有足够的实例帮助理解
6. **练习合理**（soft）：练习建议是否合理

请输出 JSON 格式：
{{
  "verdict": "passed/passed_with_notes/not_passed",
  "checks": [
    {{"name": "检查项", "severity": "hard/soft", "passed": true/false, "details": "说明", "fix_action": "修复建议"}}
  ],
  "failed_hard": 0,
  "failed_soft": 0,
  "summary": "审计总结"
}}
"""

QUIZ_AUDIT_PROMPT = """你是学习质量审计专家，负责独立审查测验题目的质量。

请审查以下测验：

**知识点**：{node_title}
**题目列表**：
{questions}

审查标准：
1. **答案正确**（hard）：重新求解每道题，验证答案是否正确
2. **题目清晰**（hard）：题目表述是否清晰无歧义
3. **选项合理**（soft）：选择题的干扰项是否合理
4. **难度分布**（soft）：题目难度是否符合要求分布
5. **知识覆盖**（soft）：是否覆盖了关键知识点
6. **解析完整**（soft）：解析是否详细易懂

请输出 JSON 格式：
{{
  "verdict": "passed/passed_with_notes/not_passed",
  "checks": [
    {{"name": "检查项", "severity": "hard/soft", "passed": true/false, "details": "说明", "fix_action": "修复建议"}}
  ],
  "failed_hard": 0,
  "failed_soft": 0,
  "summary": "审计总结"
}}
"""


class AuditTool(BaseTool):
    """审计工具"""
    name: str = "audit"
    description: str = "审计知识图谱、教材或测验的质量"
    args_schema: Type[BaseModel] = AuditInput

    def _run(self, audit_type: str, artifact: dict, context: dict = None) -> dict:
        context = context or {}

        if audit_type == "knowledge_tree":
            return self._audit_knowledge_tree(artifact, context)
        elif audit_type == "content":
            return self._audit_content(artifact, context)
        elif audit_type == "quiz":
            return self._audit_quiz(artifact, context)
        else:
            raise ValueError(f"Unknown audit type: {audit_type}")

    def _audit_knowledge_tree(self, artifact: dict, context: dict) -> dict:
        nodes_str = "\n".join([
            f"- {n.get('node_key')}: {n.get('title')} (level={n.get('level')}, prereqs={n.get('prerequisites', [])})"
            for n in artifact.get("nodes", [])
        ])

        prompt = ChatPromptTemplate.from_template(KNOWLEDGE_TREE_AUDIT_PROMPT)
        chain = prompt | audit_llm | JsonOutputParser()

        result = chain.invoke({
            "subject": context.get("subject", ""),
            "goal": context.get("goal", ""),
            "nodes": nodes_str
        })

        # 统计失败数
        checks = result.get("checks", [])
        result["failed_hard"] = sum(1 for c in checks if c.get("severity") == "hard" and not c.get("passed"))
        result["failed_soft"] = sum(1 for c in checks if c.get("severity") == "soft" and not c.get("passed"))

        return result

    def _audit_content(self, artifact: dict, context: dict) -> dict:
        content_str = "\n".join([
            f"## {s.get('heading')}\n{s.get('content', '')}"
            for s in artifact.get("sections", [])
        ])

        prompt = ChatPromptTemplate.from_template(CONTENT_AUDIT_PROMPT)
        chain = prompt | audit_llm | JsonOutputParser()

        result = chain.invoke({
            "node_title": context.get("node_title", ""),
            "title": artifact.get("title", ""),
            "content": content_str[:3000]  # 限制长度
        })

        checks = result.get("checks", [])
        result["failed_hard"] = sum(1 for c in checks if c.get("severity") == "hard" and not c.get("passed"))
        result["failed_soft"] = sum(1 for c in checks if c.get("severity") == "soft" and not c.get("passed"))

        return result

    def _audit_quiz(self, artifact: dict, context: dict) -> dict:
        questions_str = "\n".join([
            f"Q{i+1} [{q.get('type')}]: {q.get('content')}\n答案: {q.get('answer')}"
            for i, q in enumerate(artifact.get("questions", []))
        ])

        prompt = ChatPromptTemplate.from_template(QUIZ_AUDIT_PROMPT)
        chain = prompt | audit_llm | JsonOutputParser()

        result = chain.invoke({
            "node_title": context.get("node_title", ""),
            "questions": questions_str
        })

        checks = result.get("checks", [])
        result["failed_hard"] = sum(1 for c in checks if c.get("severity") == "hard" and not c.get("passed"))
        result["failed_soft"] = sum(1 for c in checks if c.get("severity") == "soft" and not c.get("passed"))

        return result


# 实例化工具
audit_tool = AuditTool()
