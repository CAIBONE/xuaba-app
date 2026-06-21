"""测验相关 Schema"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    """单个题目"""
    type: str = Field(..., description="choice/fill/short_answer")
    content: str
    options: Optional[list[str]] = None
    answer: str
    explanation: str = ""
    difficulty: str = "normal"


class QuizBase(BaseModel):
    quiz_type: str = Field(..., description="pre_test/post_test/review/practice")
    questions: list[QuestionItem] = []


class QuizCreate(QuizBase):
    node_id: int
    user_id: int


class QuizResponse(QuizBase):
    id: int
    node_id: int
    user_id: int
    total_questions: int
    correct_count: int
    score: float
    answers_json: dict
    mastery_before: float
    mastery_after: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateQuizRequest(BaseModel):
    """生成测验请求"""
    node_id: int
    quiz_type: str = Field(default="post_test", description="pre_test/post_test/review/practice")
    question_count: int = Field(default=5, ge=1, le=20)


class SubmitQuizRequest(BaseModel):
    """提交测验答案"""
    answers: list[dict] = Field(..., description="[{question_index, answer}]")


class QuizResultResponse(BaseModel):
    """测验结果"""
    quiz_id: int
    total_questions: int
    correct_count: int
    score: float
    mastery_before: float
    mastery_after: float
    mastery_change: float
    answers_detail: list[dict]
