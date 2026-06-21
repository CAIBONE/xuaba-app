"""Pydantic Schemas 汇总"""
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserProfile,
    LoginRequest, LoginResponse
)
from app.schemas.project import (
    ProjectBase, ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
)
from app.schemas.node import (
    NodeBase, NodeCreate, NodeUpdate, NodeResponse, NodeListResponse, KnowledgeTreeResponse
)
from app.schemas.content import (
    ContentBase, ContentCreate, ContentUpdate, ContentResponse, ContentListResponse,
    GenerateContentRequest, PushContentRequest
)
from app.schemas.quiz import (
    QuestionItem, QuizBase, QuizCreate, QuizResponse,
    GenerateQuizRequest, SubmitQuizRequest, QuizResultResponse
)
from app.schemas.schedule import (
    ScheduleBase, ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleListResponse,
    GeneratePlanRequest, PlanStrategy
)
from app.schemas.report import (
    ProgressReport, MasteryPoint, MasteryReport,
    HeatmapDay, HeatmapReport,
    ForgettingPoint, ForgettingReport,
    WeakNode, WeakNodesReport
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserProfile",
    "LoginRequest", "LoginResponse",
    # Project
    "ProjectBase", "ProjectCreate", "ProjectUpdate", "ProjectResponse", "ProjectListResponse",
    # Node
    "NodeBase", "NodeCreate", "NodeUpdate", "NodeResponse", "NodeListResponse", "KnowledgeTreeResponse",
    # Content
    "ContentBase", "ContentCreate", "ContentUpdate", "ContentResponse", "ContentListResponse",
    "GenerateContentRequest", "PushContentRequest",
    # Quiz
    "QuestionItem", "QuizBase", "QuizCreate", "QuizResponse",
    "GenerateQuizRequest", "SubmitQuizRequest", "QuizResultResponse",
    # Schedule
    "ScheduleBase", "ScheduleCreate", "ScheduleUpdate", "ScheduleResponse", "ScheduleListResponse",
    "GeneratePlanRequest", "PlanStrategy",
    # Report
    "ProgressReport", "MasteryPoint", "MasteryReport",
    "HeatmapDay", "HeatmapReport",
    "ForgettingPoint", "ForgettingReport",
    "WeakNode", "WeakNodesReport",
]
