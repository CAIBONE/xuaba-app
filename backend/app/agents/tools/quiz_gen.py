"""测验生成工具"""
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.agents.llm import llm


class QuizQuestion(BaseModel):
    """测验题目"""
    type: str = Field(description="题型：choice/fill/short_answer")
    content: str = Field(description="题目内容")
    options: list[str] = Field(default_factory=list, description="选项（选择题）")
    answer: str = Field(description="正确答案")
    explanation: str = Field(description="解析")
    difficulty: str = Field(default="normal", description="难度")


class GenerateQuizInput(BaseModel):
    """测验生成输入"""
    node_title: str = Field(description="知识节点标题")
    node_content: str = Field(description="教材内容（用于出题）")
    quiz_type: str = Field(default="post_test", description="类型：pre_test/post_test/review/practice")
    question_count: int = Field(default=5, description="题目数量")


class GenerateQuizOutput(BaseModel):
    """测验生成输出"""
    questions: list[QuizQuestion] = Field(description="题目列表")
    total_score: int = Field(description="总分")
    passing_score: int = Field(description="及格分")


QUIZ_PROMPT = """你是一位出题专家，擅长设计能真正检验学习效果的题目。

请根据以下知识内容生成测验题：

**知识点**：{node_title}
**教材内容**：
{node_content}

**测验类型**：{quiz_type}
**题目数量**：{question_count} 道

题型要求：
- 选择题：3-4 个选项，只有一个正确答案
- 填空题：关键概念填空
- 简答题：检验理解深度

难度分布：
- 基础题 40%：直接考察知识点
- 中等题 40%：需要理解和应用
- 进阶题 20%：需要分析和综合

请输出 JSON 格式：
{{
  "questions": [
    {{
      "type": "choice",
      "content": "题目内容",
      "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
      "answer": "A",
      "explanation": "解析说明",
      "difficulty": "easy/normal/hard"
    }}
  ],
  "total_score": 100,
  "passing_score": 60
}}
"""


class GenerateQuizTool(BaseTool):
    """测验生成工具"""
    name: str = "generate_quiz"
    description: str = "根据教材内容生成测验题目"
    args_schema: Type[BaseModel] = GenerateQuizInput

    def _run(
        self,
        node_title: str,
        node_content: str,
        quiz_type: str = "post_test",
        question_count: int = 5
    ) -> dict:
        quiz_type_desc = {
            "pre_test": "课前预习检测，考察先备知识",
            "post_test": "课后测验，全面考察本节内容",
            "review": "复习测验，考察记忆和理解",
            "practice": "练习测验，侧重应用"
        }.get(quiz_type, "课后测验")

        # 限制内容长度，避免超出 token 限制
        content_preview = node_content[:2000] + "..." if len(node_content) > 2000 else node_content

        prompt = ChatPromptTemplate.from_template(QUIZ_PROMPT)
        chain = prompt | llm | JsonOutputParser()

        result = chain.invoke({
            "node_title": node_title,
            "node_content": content_preview,
            "quiz_type": quiz_type_desc,
            "question_count": question_count
        })

        # 设置默认分值
        if "total_score" not in result:
            result["total_score"] = 100
        if "passing_score" not in result:
            result["passing_score"] = 60

        return result


# 实例化工具
generate_quiz = GenerateQuizTool()
