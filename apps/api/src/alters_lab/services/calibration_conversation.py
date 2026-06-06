"""Calibration conversation service — LLM-driven data extraction via chat."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from alters_lab.schemas.calibration_conversation import (
    BehaviorMetricsExtract,
    CalibrationConversation,
    CalibrationDraft,
    ConversationMessage,
    ExternalEvidenceExtract,
    OutcomeTargetExtract,
    PredictorProfileExtract,
)
from alters_lab.schemas.calibration_loop import CalibrationScoreValues
from alters_lab.schemas.provider_gateway import ProviderGatewayRequest
from alters_lab.services.p6_runtime import (
    generate_record_id,
    list_records,
    read_record,
    utc_now,
    write_record,
)


SYSTEM_PROMPT = """你是一个校准对话助手。你的任务是通过自然对话帮助用户完成每周的行为指标记录和校准评分。

你需要提取的数据：

1. Behavior Metrics（本周行为指标）：
   - career_education_deep_work_minutes: 深度工作/学习分钟数
   - planned_commitment_follow_through_rate: 计划执行率 (0.0-1.0)
   - expense_logged_days: 记账天数 (0-7)
   - regular_sleep_nights: 规律睡眠天数 (0-7)
   - moderate_vigorous_activity_minutes: 中高强度运动分钟数
   - avoidable_health_risk_events: 不必要的健康风险事件次数
   - meaningful_social_contact_count: 有意义社交次数
   - abandoned_committed_blocks: 放弃已承诺任务的次数
   - key_milestone_progress_pct: 关键里程碑进度 (0.0-1.0)

2. Rubric Scores（校准评分，1-5 分）：
   - execution_discipline: 执行纪律
   - exploration_freedom: 探索自由度
   - life_state_match: 生活状态匹配度
   - energy_level: 精力水平

3. External Evidence（外部证据）：
   当用户提到真实世界发生的事情时，提取为 external evidence：
   - domain: 属于哪个生活领域
   - evidence_type: 证据类型
   - description: 描述
   - objective_strength: weak/moderate/strong
   - polarity: positive/negative/neutral/mixed

4. Outcome Targets（结果目标）：
   当用户谈论未来目标或计划时，帮助他们定义可测量的 outcome target：
   - domain: 属于哪个生活领域
   - outcome_name: 目标名称
   - objective_definition: 客观定义（怎样算达成）
   - success_threshold: 成功阈值
   - measurement_method: 怎么测量
   - horizon_months: 目标时间范围 (1-24 月)

5. Predictor Profile（预测者画像）：
   当用户描述自己的性格、处境时，提取为 trait baseline 和 current context：
   - Big Five traits (0.0-1.0)
   - education/employment/financial/relationship status
   - health constraints

对话风格：
- 自然、友好，不要像填表
- 从用户的自然描述中识别数据
- 不确定的数值用范围确认
- 不要一次问所有问题，根据对话自然推进

当你识别到可以提取的结构化数据时，在回答末尾输出：

<extraction>
{
  "behavior_metrics": { ... },
  "rubric_scores": { ... },
  "external_evidence": [ ... ],
  "outcome_targets": [ ... ],
  "predictor_profile": { ... },
  "extraction_confidence": "high|medium|low",
  "reasoning": "为什么提取了这些值"
}
</extraction>

规则：
- 只在有明确数据时输出 extraction block
- 不要猜测数值——如果用户没提到，不要填
- extraction_confidence 反映你对提取准确度的判断
- 如果用户说的模糊，confidence 应该是 low 或 medium
- 只输出 JSON，不要在 extraction block 内加注释
"""

_MOCK_LLM_REPLY = "这周怎么样？工作、学习、生活各方面有什么想分享的吗？"


def _extract_json_from_llm_output(llm_output: str) -> dict | None:
    """Extract structured data from LLM output using <extraction> tags."""
    match = re.search(
        r"<extraction>\s*(\{.*?\})\s*</extraction>",
        llm_output,
        re.DOTALL,
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _build_draft_from_extraction(
    extraction: dict,
    conversation_id: str,
    llm_model: str | None = None,
) -> CalibrationDraft | None:
    """Build a CalibrationDraft from parsed extraction JSON."""
    if not extraction:
        return None

    behavior = None
    if extraction.get("behavior_metrics"):
        try:
            behavior = BehaviorMetricsExtract(**extraction["behavior_metrics"])
        except Exception:
            pass

    rubric = None
    if extraction.get("rubric_scores"):
        try:
            rubric = CalibrationScoreValues(**extraction["rubric_scores"])
        except Exception:
            pass

    evidence_list = []
    for ev in extraction.get("external_evidence", []):
        try:
            evidence_list.append(ExternalEvidenceExtract(**ev))
        except Exception:
            pass

    target_list = []
    for ot in extraction.get("outcome_targets", []):
        try:
            target_list.append(OutcomeTargetExtract(**ot))
        except Exception:
            pass

    predictor = None
    if extraction.get("predictor_profile"):
        try:
            predictor = PredictorProfileExtract(**extraction["predictor_profile"])
        except Exception:
            pass

    # Only create draft if we extracted something
    if not behavior and not rubric and not evidence_list and not target_list and not predictor:
        return None

    return CalibrationDraft(
        conversation_id=conversation_id,
        behavior_metrics=behavior,
        rubric_scores=rubric,
        external_evidence=evidence_list,
        outcome_targets=target_list,
        predictor_profile=predictor,
        llm_model=llm_model,
        extraction_confidence=extraction.get("extraction_confidence", "low"),
        llm_reasoning=extraction.get("reasoning", ""),
    )


def _draft_path(draft_id: str, repo_root: Path | None = None) -> Path:
    from alters_lab.services.p6_runtime import runtime_dir

    return runtime_dir("calibration_drafts", repo_root=repo_root) / f"{draft_id}.yaml"


def _conversation_path(
    conversation_id: str, repo_root: Path | None = None
) -> Path:
    from alters_lab.services.p6_runtime import runtime_dir

    return (
        runtime_dir("calibration_conversations", repo_root=repo_root)
        / f"{conversation_id}.yaml"
    )


def _ensure_dirs(repo_root: Path | None = None) -> None:
    from alters_lab.services.p6_runtime import runtime_dir

    runtime_dir("calibration_drafts", repo_root=repo_root).mkdir(
        parents=True, exist_ok=True
    )
    runtime_dir("calibration_conversations", repo_root=repo_root).mkdir(
        parents=True, exist_ok=True
    )


def _build_messages_for_llm(
    conversation: CalibrationConversation,
    user_message: str,
) -> list[dict]:
    """Build the messages list for the LLM API call."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation.messages:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})
    return messages


def _call_llm(
    messages: list[dict], repo_root: Path | None = None
) -> tuple[str, str | None]:
    """Call LLM via provider gateway. Returns (reply_content, model_name)."""
    from alters_lab.services.provider_gateway import provider_gateway_complete

    request = ProviderGatewayRequest(
        messages=messages,
        caller="calibration_conversation",
    )
    response = provider_gateway_complete(request)
    return response.content, (
        response.model if response.status != "mock_response" else None
    )


def _load_conversation(
    conversation_id: str, repo_root: Path | None = None
) -> CalibrationConversation:
    """Load a conversation from disk."""
    path = _conversation_path(conversation_id, repo_root=repo_root)
    if not path.exists():
        raise FileNotFoundError(f"Conversation not found: {conversation_id}")
    from alters_lab.services import io

    data = io.read_yaml(path)
    return CalibrationConversation(**data)


def _save_conversation(
    conversation: CalibrationConversation, repo_root: Path | None = None
) -> Path:
    """Save a conversation to disk."""
    _ensure_dirs(repo_root=repo_root)
    path = _conversation_path(
        conversation.conversation_id, repo_root=repo_root
    )
    from alters_lab.services import io

    io.write_yaml(
        path, conversation.model_dump(), sort_keys=False, allow_unicode=True
    )
    return path


def _save_draft(draft: CalibrationDraft, repo_root: Path | None = None) -> Path:
    """Save a draft to disk."""
    _ensure_dirs(repo_root=repo_root)
    path = _draft_path(draft.draft_id, repo_root=repo_root)
    from alters_lab.services import io

    io.write_yaml(
        path, draft.model_dump(), sort_keys=False, allow_unicode=True
    )
    return path


def _load_draft(
    draft_id: str, repo_root: Path | None = None
) -> CalibrationDraft:
    """Load a draft from disk."""
    path = _draft_path(draft_id, repo_root=repo_root)
    if not path.exists():
        raise FileNotFoundError(f"Draft not found: {draft_id}")
    from alters_lab.services import io

    data = io.read_yaml(path)
    return CalibrationDraft(**data)


# --- Public API ---


def start_conversation(
    branch_id: str | None = None,
    repo_root: Path | None = None,
) -> CalibrationConversation:
    """Start a new calibration conversation."""
    _ensure_dirs(repo_root=repo_root)
    conversation = CalibrationConversation()
    conversation.messages.append(
        ConversationMessage(role="assistant", content=_MOCK_LLM_REPLY)
    )
    _save_conversation(conversation, repo_root=repo_root)
    return conversation


def send_message(
    conversation_id: str,
    user_message: str,
    repo_root: Path | None = None,
) -> tuple[CalibrationConversation, CalibrationDraft | None]:
    """Send a user message and get LLM reply. Returns (conversation, draft_or_none)."""
    conversation = _load_conversation(conversation_id, repo_root=repo_root)

    if conversation.status != "active":
        raise ValueError("Conversation is not active")

    # Add user message
    conversation.messages.append(
        ConversationMessage(role="user", content=user_message)
    )

    # Build messages for LLM
    llm_messages = _build_messages_for_llm(conversation, user_message)

    # Call LLM
    reply_content, model_name = _call_llm(llm_messages, repo_root=repo_root)

    # Add assistant reply
    conversation.messages.append(
        ConversationMessage(role="assistant", content=reply_content)
    )

    # Try to extract structured data
    extraction = _extract_json_from_llm_output(reply_content)
    draft = _build_draft_from_extraction(
        extraction, conversation.conversation_id, llm_model=model_name
    )

    if draft:
        _save_draft(draft, repo_root=repo_root)
        conversation.draft_ids.append(draft.draft_id)

    _save_conversation(conversation, repo_root=repo_root)

    return conversation, draft


def get_conversation(
    conversation_id: str,
    repo_root: Path | None = None,
) -> CalibrationConversation:
    """Load a conversation by ID."""
    return _load_conversation(conversation_id, repo_root=repo_root)


def list_drafts(
    status: str | None = None,
    repo_root: Path | None = None,
) -> list[CalibrationDraft]:
    """List all drafts, optionally filtered by status."""
    from alters_lab.services import io
    from alters_lab.services.p6_runtime import runtime_dir

    drafts_dir = runtime_dir("calibration_drafts", repo_root=repo_root)
    if not drafts_dir.exists():
        return []

    drafts = []
    for path in sorted(drafts_dir.glob("*.yaml")):
        data = io.read_yaml(path)
        draft = CalibrationDraft(**data)
        if status is None or draft.status == status:
            drafts.append(draft)

    return drafts


def get_draft(
    draft_id: str,
    repo_root: Path | None = None,
) -> CalibrationDraft:
    """Load a draft by ID."""
    return _load_draft(draft_id, repo_root=repo_root)


def confirm_draft(
    draft_id: str,
    corrections: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> CalibrationDraft:
    """Confirm a draft and write behavior_metrics + calibration scores."""
    draft = _load_draft(draft_id, repo_root=repo_root)

    if draft.status != "pending":
        raise ValueError(f"Draft is not pending (status: {draft.status})")

    if corrections:
        draft.user_corrections = corrections

    # Write behavior metrics if present
    if draft.behavior_metrics:
        from alters_lab.schemas.behavior_metrics_record import (
            WeeklyBehaviorMetricsRecord,
        )

        bm = draft.behavior_metrics
        week_start_str = bm.week_start or utc_now()[:10]
        week_end_str = bm.week_end or utc_now()[:10]

        record = WeeklyBehaviorMetricsRecord(
            record_id=generate_record_id("bm"),
            week_start=date.fromisoformat(week_start_str),
            week_end=date.fromisoformat(week_end_str),
            branch_id=bm.branch_id,
            career_education_deep_work_minutes=bm.career_education_deep_work_minutes
            or 0,
            planned_commitment_follow_through_rate=bm.planned_commitment_follow_through_rate
            or 0.0,
            expense_logged_days=bm.expense_logged_days or 0,
            regular_sleep_nights=bm.regular_sleep_nights or 0,
            moderate_vigorous_activity_minutes=bm.moderate_vigorous_activity_minutes
            or 0,
            avoidable_health_risk_events=bm.avoidable_health_risk_events or 0,
            meaningful_social_contact_count=bm.meaningful_social_contact_count or 0,
            abandoned_committed_blocks=bm.abandoned_committed_blocks or 0,
            key_milestone_progress_pct=bm.key_milestone_progress_pct or 0.0,
            notes=bm.notes,
        )

        data = record.model_dump()
        data["week_start"] = str(data["week_start"])
        data["week_end"] = str(data["week_end"])
        write_record("behavior_metrics", record.record_id, data, repo_root)

    # Write calibration score if present
    if draft.rubric_scores:
        from alters_lab.schemas.calibration_loop import (
            CalibrationInputRefs,
            CalibrationLoopBoundaryConfirmations,
            RealityScoreRecord,
        )
        from alters_lab.services import io as alters_io
        from alters_lab.services.p6_runtime import runtime_dir

        score_id = generate_record_id("score")
        score_record = RealityScoreRecord(
            id=score_id,
            status="recorded",
            created_at=utc_now(),
            branch_id=(
                (draft.behavior_metrics.branch_id or "branch_A")
                if draft.behavior_metrics
                else "branch_A"
            ),
            alter_id="alter_A",
            input_refs=CalibrationInputRefs(alter_ref="alter_A"),
            actual_scores=draft.rubric_scores,
            submitted_by_user=True,
            source="llm_calibration_draft",
            caller="calibration_conversation",
            boundary_confirmations=CalibrationLoopBoundaryConfirmations(),
        )

        scores_dir = runtime_dir("calibration_records", repo_root=repo_root)
        scores_dir.mkdir(parents=True, exist_ok=True)
        score_path = scores_dir / f"{score_id}.yaml"
        alters_io.write_yaml(
            score_path,
            score_record.model_dump(),
            sort_keys=False,
            allow_unicode=True,
        )

    # Write external evidence if present
    for ev_extract in draft.external_evidence:
        from alters_lab.schemas.external_evidence import ExternalEvidenceRecord

        evidence = ExternalEvidenceRecord(
            domain=ev_extract.domain,
            evidence_type=ev_extract.evidence_type,
            description=ev_extract.description,
            objective_strength=ev_extract.objective_strength,
            polarity=ev_extract.polarity,
            numeric_value=ev_extract.numeric_value,
            unit=ev_extract.unit,
        )

        data = evidence.model_dump()
        write_record("external_evidence", evidence.evidence_id, data, repo_root)

    # Write outcome targets if present
    for ot_extract in draft.outcome_targets:
        from alters_lab.schemas.branch_outcome_targets import BranchOutcomeTargetRecord

        target = BranchOutcomeTargetRecord(
            target_id=generate_record_id("bot"),
            branch_id=ot_extract.branch_id or "branch_A",
            milestone_id=ot_extract.milestone_id,
            domain=ot_extract.domain,
            horizon_months=ot_extract.horizon_months,
            outcome_name=ot_extract.outcome_name,
            objective_definition=ot_extract.objective_definition,
            success_threshold=ot_extract.success_threshold,
            measurement_method=ot_extract.measurement_method,
            baseline_value=ot_extract.baseline_value,
            target_value=ot_extract.target_value,
            created_at=utc_now(),
        )

        data = target.model_dump()
        data["created_at"] = str(data["created_at"])
        write_record("branch_outcome_targets", target.target_id, data, repo_root)

    # Write predictor profile if present
    if draft.predictor_profile:
        from alters_lab.schemas.predictor_profile import (
            CurrentContext,
            PredictorProfileRecord,
            PredictionTargets,
            TraitBaseline,
        )

        pp = draft.predictor_profile
        profile = PredictorProfileRecord(
            profile_id=generate_record_id("pp"),
            created_at=utc_now(),
            trait_baseline=TraitBaseline(
                conscientiousness=pp.conscientiousness,
                neuroticism_negative_emotionality=pp.neuroticism_negative_emotionality,
                extraversion=pp.extraversion,
                agreeableness=pp.agreeableness,
                openness=pp.openness,
                source=pp.trait_source,
            ),
            current_context=CurrentContext(
                education_status=pp.education_status,
                employment_status=pp.employment_status,
                financial_stability=pp.financial_stability,
                relationship_status=pp.relationship_status,
                health_constraints=pp.health_constraints,
            ),
            prediction_targets=PredictionTargets(
                target_domains=pp.target_domains,
                time_horizon_months=pp.time_horizon_months,
            ),
            limitations=pp.limitations,
        )

        data = profile.model_dump()
        data["created_at"] = str(data["created_at"])
        write_record("predictor_profiles", profile.profile_id, data, repo_root)

    # Mark draft as confirmed
    draft.status = "confirmed"
    draft.confirmed_at = utc_now()
    _save_draft(draft, repo_root=repo_root)

    return draft


def reject_draft(
    draft_id: str,
    repo_root: Path | None = None,
) -> CalibrationDraft:
    """Reject a draft."""
    draft = _load_draft(draft_id, repo_root=repo_root)

    if draft.status != "pending":
        raise ValueError(f"Draft is not pending (status: {draft.status})")

    draft.status = "rejected"
    _save_draft(draft, repo_root=repo_root)
    return draft
