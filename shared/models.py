"""Data models for OrchestRAI."""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"


class WorkflowStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    confidence: float


class ScriptSegment(BaseModel):
    text: str
    duration: float
    source_timestamps: Optional[Dict[str, float]] = None
    emphasis: str = "medium"


class ScriptOutput(BaseModel):
    content_id: str
    script_id: str
    hook: ScriptSegment
    scenes: List[ScriptSegment]
    cta: ScriptSegment
    total_duration: float
    version: int = 1


class TranslatedScript(BaseModel):
    language: str
    hook: str
    scenes: List[str]
    cta: str
    cultural_flags: List[str] = []


class ScenePlan(BaseModel):
    scene_number: int
    visual_description: str
    source_timestamp: Dict[str, float]
    asset_type: str
    transition: str
    duration: float
    text_overlay: Optional[Dict[str, str]] = None


class QualityScores(BaseModel):
    semantic_alignment: float
    pacing: float
    readability: float
    cultural_appropriateness: float


class CriticFeedback(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    critical_issues: List[str]


class AICriticOutput(BaseModel):
    content_id: str
    evaluation_id: str
    scores: QualityScores
    overall_score: float
    feedback: CriticFeedback
    timestamp: str
