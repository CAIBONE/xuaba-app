"""知识图谱生成工具"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.agents.llm import llm


class KnowledgeNode(BaseModel):
    """知识节点"""
    node_key: str = Field(description="节点标识，如 mod-01-01")
    title: str = Field(description="节点标题")
    parent_key: str = Field(default="", description="父节点标识，根节点为空")
    level: int = Field(description="层级，0 为根")
    estimated_minutes: int = Field(description="预计学习时间（分钟）")
    prerequisites: list[str] = Field(default_factory=list, description="前置节点标识列表")


class KnowledgeTreeInput(BaseModel):
    """知识图谱生成输入"""
    subject: str = Field(description="学习科目")
    goal: str = Field(description="学习目标")
    goal_type: str = Field(default="skill", description="目标类型：exam/skill/interest")


class KnowledgeTreeOutput(BaseModel):
    """知识图谱生成输出"""
    nodes: list[KnowledgeNode] = Field(description="知识节点列表")
    total_hours: float = Field(description="预计总学时（小时）")


KNOWLEDGE_TREE_PROMPT = """你是一个专业的教育专家，擅长设计知识体系结构。

请根据以下信息，设计一个完整的知识图谱：

**科目**：{subject}
**学习目标**：{goal}
**目标类型**：{goal_type}

要求：
1. 从基础到进阶，循序渐进
2. 每个节点有明确的 prerequisites（前置依赖）
3. 每个节点预估学习时间（分钟）
4. 节点命名清晰，能看出知识关系
5. 总节点数控制在 15-30 个

请输出 JSON 格式的知识节点列表，每个节点包含：
- node_key: 节点标识（如 mod-01-01）
- title: 节点标题
- parent_key: 父节点标识（根节点为空字符串）
- level: 层级（0 为根）
- estimated_minutes: 预计学习时间（分钟）
- prerequisites: 前置节点标识列表

输出格式：
{{"nodes": [...], "total_hours": 0.0}}
"""


class GenerateKnowledgeTreeTool(BaseTool):
    """知识图谱生成工具"""
    name: str = "generate_knowledge_tree"
    description: str = "根据科目和学习目标生成知识图谱结构"
    args_schema: Type[BaseModel] = KnowledgeTreeInput

    def _run(
        self,
        subject: str,
        goal: str,
        goal_type: str = "skill"
    ) -> dict:
        prompt = ChatPromptTemplate.from_template(KNOWLEDGE_TREE_PROMPT)
        chain = prompt | llm | JsonOutputParser()

        result = chain.invoke({
            "subject": subject,
            "goal": goal,
            "goal_type": goal_type
        })

        # 计算总学时
        total_minutes = sum(n.get("estimated_minutes", 30) for n in result.get("nodes", []))
        result["total_hours"] = round(total_minutes / 60, 1)

        return result


# 实例化工具
generate_knowledge_tree = GenerateKnowledgeTreeTool()
