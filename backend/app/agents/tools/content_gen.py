"""教材生成工具"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.agents.llm import llm


class ContentSection(BaseModel):
    """教材章节"""
    heading: str = Field(description="章节标题")
    content: str = Field(description="章节内容（Markdown 格式）")


class GenerateContentInput(BaseModel):
    """教材生成输入"""
    node_title: str = Field(description="知识节点标题")
    node_description: str = Field(default="", description="节点描述")
    content_type: str = Field(default="lesson", description="类型：lesson/summary/exercise/example")
    difficulty: str = Field(default="normal", description="难度：easy/normal/hard")
    estimated_minutes: int = Field(default=30, description="预计阅读时间（分钟）")


class GenerateContentOutput(BaseModel):
    """教材生成输出"""
    title: str = Field(description="教材标题")
    sections: list[ContentSection] = Field(description="章节列表")
    word_count: int = Field(description="总字数")
    key_points: list[str] = Field(description="核心知识点")
    practice_suggestions: list[str] = Field(default_factory=list, description="练习建议")


CONTENT_PROMPT = """你是一位经验丰富的教师，擅长将复杂知识讲解得通俗易懂。

请为以下知识点生成一份教材：

**知识点**：{node_title}
**描述**：{node_description}
**教材类型**：{content_type}
**难度级别**：{difficulty}
**预计阅读时间**：{estimated_minutes} 分钟

要求：
1. 内容按阅读密度 250-300 字/分钟设计
2. 结构清晰，有层次递进
3. 包含实例和类比帮助理解
4. 末尾有总结和练习建议
5. 使用 Markdown 格式

请输出 JSON 格式：
{{
  "title": "教材标题",
  "sections": [
    {{"heading": "章节标题", "content": "章节内容（Markdown）"}}
  ],
  "word_count": 0,
  "key_points": ["核心知识点1", "核心知识点2"],
  "practice_suggestions": ["练习建议1", "练习建议2"]
}}
"""


class GenerateContentTool(BaseTool):
    """教材生成工具"""
    name: str = "generate_content"
    description: str = "根据知识节点生成学习教材"
    args_schema: Type[BaseModel] = GenerateContentInput

    def _run(
        self,
        node_title: str,
        node_description: str = "",
        content_type: str = "lesson",
        difficulty: str = "normal",
        estimated_minutes: int = 30
    ) -> dict:
        # 根据难度调整提示
        difficulty_desc = {
            "easy": "入门级，假设读者零基础",
            "normal": "标准难度，适合大多数学习者",
            "hard": "进阶难度，需要一定基础"
        }.get(difficulty, "标准难度")

        prompt = ChatPromptTemplate.from_template(CONTENT_PROMPT)
        chain = prompt | llm | JsonOutputParser()

        result = chain.invoke({
            "node_title": node_title,
            "node_description": node_description or node_title,
            "content_type": content_type,
            "difficulty": difficulty_desc,
            "estimated_minutes": estimated_minutes
        })

        # 计算字数
        total_content = " ".join(s.get("content", "") for s in result.get("sections", []))
        result["word_count"] = len(total_content)

        return result


# 实例化工具
generate_content = GenerateContentTool()
