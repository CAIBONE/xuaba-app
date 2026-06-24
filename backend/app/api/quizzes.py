"""测验 API"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.node import Node
from app.models.quiz import Quiz
from app.models.mastery_history import MasteryHistory
from app.schemas.quiz import QuizCreate, QuizResponse, GenerateQuizRequest, SubmitQuizRequest, QuizResultResponse
from app.api.auth import get_current_user
from app.services.quiz_generator import generate_quiz as generate_quiz_service

router = APIRouter()


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    data: GenerateQuizRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    生成测验（调用 LLM）
    """
    # 验证节点存在
    result = await db.execute(select(Node).where(Node.id == data.node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    # 获取当前掌握度
    mastery_before = float(node.mastery_level)

    # 调用 LLM 生成测验
    try:
        quiz_data = await generate_quiz_service(
            node_title=node.title,
            node_description=node.description,
            question_count=data.question_count,
            quiz_type=data.quiz_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测验生成失败: {str(e)}")

    questions = quiz_data.get("questions", [])

    quiz = Quiz(
        node_id=data.node_id,
        user_id=user.id,
        quiz_type=data.quiz_type,
        questions=questions,
        total_questions=len(questions),
        mastery_before=mastery_before,
    )
    db.add(quiz)
    await db.flush()
    await db.refresh(quiz)
    return QuizResponse.model_validate(quiz)


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取测验详情"""
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user.id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="测验不存在")
    return QuizResponse.model_validate(quiz)


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: int,
    data: SubmitQuizRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    提交测验答案

    流程：
    1. 验证答案正确性
    2. 计算得分
    3. 更新掌握度
    4. 记录掌握度历史
    """
    # 获取测验
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user.id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="测验不存在")

    if quiz.completed_at:
        raise HTTPException(status_code=400, detail="测验已提交")

    # 验证答案
    questions = quiz.questions
    answers_detail = []
    correct_count = 0

    for answer in data.answers:
        q_index = answer.get("question_index", 0)
        user_answer = answer.get("answer", "")

        if q_index < len(questions):
            correct_answer = questions[q_index].get("answer", "")
            is_correct = user_answer.upper() == correct_answer.upper()
            if is_correct:
                correct_count += 1

            answers_detail.append({
                "question_index": q_index,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

    # 计算得分
    total_questions = len(questions)
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0

    # 计算掌握度变化
    mastery_before = float(quiz.mastery_before)
    mastery_change = (score / 100 - mastery_before) * 0.3  # 简单算法
    mastery_after = min(1.0, mastery_before + mastery_change)

    # 更新测验记录
    quiz.correct_count = correct_count
    quiz.score = score
    quiz.answers_json = {"details": answers_detail}
    quiz.mastery_after = mastery_after
    quiz.started_at = quiz.started_at or datetime.utcnow()
    quiz.completed_at = datetime.utcnow()

    # 更新节点掌握度
    result = await db.execute(select(Node).where(Node.id == quiz.node_id))
    node = result.scalar_one_or_none()
    if node:
        node.mastery_level = mastery_after

        # 记录掌握度历史
        history = MasteryHistory(
            user_id=user.id,
            node_id=quiz.node_id,
            mastery_level=mastery_after,
            assessment_type="quiz",
        )
        db.add(history)

    await db.flush()

    return QuizResultResponse(
        quiz_id=quiz.id,
        total_questions=total_questions,
        correct_count=correct_count,
        score=round(score, 2),
        mastery_before=mastery_before,
        mastery_after=round(mastery_after, 2),
        mastery_change=round(mastery_change, 2),
        answers_detail=answers_detail
    )


@router.post("/{quiz_id}/feedback")
async def submit_quiz_feedback(
    quiz_id: int,
    feedback: dict,  # {"question_0": "confused", "question_1": "familiar", ...}
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    提交测验反馈

    feedback 格式：
    {
        "question_0": "confused",   # 不了解
        "question_1": "familiar",   # 熟知
        "question_2": "unclear"     # 题目有问题
    }

    反馈类型：
    - confused: 不了解，需要复习
    - familiar: 熟知，已掌握
    - unclear: 题目表述不清
    """
    # 获取测验
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user.id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="测验不存在")

    # 更新反馈
    quiz.feedback_json = feedback
    await db.flush()

    # 根据反馈更新用户画像
    result = await db.execute(select(User).where(User.id == user.id))
    user_obj = result.scalar_one()

    # 统计反馈
    confused_count = sum(1 for v in feedback.values() if v == "confused")
    familiar_count = sum(1 for v in feedback.values() if v == "familiar")

    # 更新用户画像（简单实现，后续可优化）
    profile = user_obj.profile_json or {}
    profile["quiz_feedback_count"] = profile.get("quiz_feedback_count", 0) + 1
    profile["total_confused"] = profile.get("total_confused", 0) + confused_count
    profile["total_familiar"] = profile.get("total_familiar", 0) + familiar_count

    # 根据反馈调整学习风格
    if confused_count > familiar_count:
        profile["learning_style"] = "需要更多基础讲解"
    elif familiar_count > confused_count:
        profile["learning_style"] = "可以快速推进"

    user_obj.profile_json = profile
    await db.flush()

    return {
        "message": "反馈已提交",
        "quiz_id": quiz_id,
        "feedback_count": len(feedback)
    }
