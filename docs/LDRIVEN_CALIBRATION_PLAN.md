# LLM-Driven Calibration — Implementation Plan

**Created:** 2026-06-04
**Status:** PLANNED — not started
**Depends on:** v1.0 (tagged and released)

---

## Problem

当前的校准流程是**用户手动填表**：

- Behavior metrics → 用户每周手动填写结构化字段
- Rubric scores → 用户在 UI 上打 1-5 分
- External evidence → 用户手动创建 evidence record
- Outcome targets → 用户手动定义

这是最大的使用障碍。用户不会持续手动填表，导致校准数据积累缓慢，系统价值无法体现。

## Goal

**LLM 作为主导者**，通过自然对话引导用户完成所有校准数据的提取：

- 用户只需聊天，不需要知道 schema 结构
- LLM 主动提问、识别数据、提取结构化信息
- LLM 在对话中自然地总结理解到的内容，用户确认或纠正
- 确认后写入系统，保持完整的 traceability

## Architecture

```
用户 ←→ LLM Conversation Service ←→ Provider Gateway ←→ LLM API
                ↓
        Structured Extraction
                ↓
        Draft Storage (pending)
                ↓
        User Confirmation
                ↓
        Write to existing schemas:
        - behavior_metrics/weekly_records
        - calibration/scores
        - external_evidence
        - outcome_targets
```

## Key Design Decisions

### 1. 提取范围（按优先级）

| 优先级 | 数据类型 | 频率 | 理由 |
|--------|---------|------|------|
| P0 | Behavior metrics + Rubric scores | 每周 | 最高频、最痛苦的填写任务 |
| P1 | External evidence | 随时 | 零散事件，最适合对话捕捉 |
| P2 | Outcome targets | 低频 | 相对静态，定义后很少改 |
| P3 | Predictor profile | 一次性 | 用户手动填一次即可 |

### 2. 对话粒度

**自由聊天，LLM 自己判断提取什么**

- 用户不会说"我要填 behavior metrics"，他们会说"这周挺累的，exercise 没怎么动"
- LLM 从自然语言中识别可提取的数据，同时维持对话连贯性
- 内部维护状态机：已提取什么、还缺什么，主动补全

### 3. Draft-then-confirm 模式

- LLM 提取的数据先存为 draft（pending 状态）
- 在对话中以聚类摘要形式确认，不是逐字段确认
- 对话结束时展示结构化总结卡片，用户确认后写入
- 前端展示 draft 卡片，用户点"确认"即写入

### 4. Provider 选择

**先用 provider_gateway + prompt-based JSON extraction，不依赖 tool_use**

- 现有架构不支持 tool_use/function_calling，加这个改动大
- Prompt-based extraction 够用：system prompt 要求 LLM 输出 `<extraction>JSON</extraction>` block
- 用标签包裹比纯 JSON 更可靠（不和对话内容混淆）
- 后续如果 extraction 准确率不够，再升级到 tool_use

### 5. Safety Constraints

- `submitted_by_user: Literal[True]` 限制不变——LLM 提取的数据必须经过用户确认才能写入
- LLM 不能自动提交 reality score，只能生成 draft
- 所有 LLM 输出标记为 unverified，直到用户确认
- Provider output 不能写入 active YAML（已有 safety flag）

---

## Phase 1: Behavior Metrics + Rubric Scores Extraction

**目标：** 用户跟 LLM 聊天，LLM 自动提取每周 behavior metrics 和 rubric 评分

### Scope

- 新建 `CalibrationConversationService`（service）
- 新建 `calibration_conversation` schema
- 新建 `calibration_conversation` API router
- 新建 system prompt 模板
- 复用 `provider_gateway` 做 LLM 调用
- 新建 draft storage（`alters/product/calibration_drafts/`）
- 新建 draft confirmation endpoint
- 前端：对话界面 + draft 确认卡片

### Schema

```python
class CalibrationDraft(BaseModel):
    draft_id: str  # auto-generated, prefix "cd"
    source_type: Literal["llm_calibration_draft"] = "llm_calibration_draft"
    created_at: str  # auto UTC
    conversation_id: str
    status: Literal["pending", "confirmed", "rejected"] = "pending"

    # Extracted data (all optional — LLM fills what it can)
    behavior_metrics: BehaviorMetricsExtract | None = None
    rubric_scores: CalibrationScoreValues | None = None

    # LLM metadata
    llm_model: str | None = None
    extraction_confidence: Literal["high", "medium", "low"] = "low"
    llm_reasoning: str = ""  # why LLM extracted these values

    # User confirmation
    confirmed_at: str | None = None
    user_corrections: dict[str, Any] = {}  # field -> corrected value


class BehaviorMetricsExtract(BaseModel):
    """Subset of WeeklyBehaviorMetricsRecord fields the LLM can extract."""
    week_start: str | None = None
    week_end: str | None = None
    branch_id: str | None = None
    career_education_deep_work_minutes: int | None = None
    planned_commitment_follow_through_rate: float | None = None
    expense_logged_days: int | None = None
    regular_sleep_nights: int | None = None
    moderate_vigorous_activity_minutes: int | None = None
    avoidable_health_risk_events: int | None = None
    meaningful_social_contact_count: int | None = None
    abandoned_committed_blocks: int | None = None
    key_milestone_progress_pct: float | None = None
    notes: str = ""
```

### API Endpoints

```
POST /calibration-conversation/start
    → 创建新对话，返回 conversation_id + LLM 的开场白

POST /calibration-conversation/{conversation_id}/message
    → 发送用户消息，返回 LLM 回复 + extraction draft（如果有）

GET /calibration-conversation/{conversation_id}/draft
    → 获取当前对话的 draft

POST /calibration-conversation/drafts/{draft_id}/confirm
    → 用户确认 draft，写入 behavior_metrics + calibration scores

POST /calibration-conversation/drafts/{draft_id}/reject
    → 用户拒绝 draft

GET /calibration-conversation/drafts
    → 列出所有 pending drafts
```

### System Prompt Design

```
你是 Alters Lab 的校准引导助手。你的任务是通过自然对话帮助用户
完成每周的行为指标记录和校准评分。

你需要提取的数据：

1. Behavior Metrics（本周行为指标）：
   - career_education_deep_work_minutes: 深度工作/学习分钟数
   - planned_commitment_follow_through_rate: 计划执行率 (0.0-1.0)
   - expense_logged_days: 记账天数 (0-7)
   - regular_sleep_nights: 规律睡眠天数 (0-7)
   - moderate_vigorous_activity_minutes: 中高强度运动分钟数
   - meaningful_social_contact_count: 有意义社交次数
   - abandoned_committed_blocks: 放弃已承诺任务的次数

2. Rubric Scores（校准评分，1-5 分）：
   - execution_discipline: 执行纪律
   - exploration_freedom: 探索自由度
   - life_state_match: 生活状态匹配度
   - energy_level: 精力水平

对话风格：
- 自然、友好，不要像填表
- 从用户的自然描述中识别数据
- 不确定的数值用范围确认："大概 2 小时左右？"
- 不要一次问所有问题，根据对话自然推进
- 如果用户提到了你无法映射到具体指标的信息，记录在 notes 里

当你识别到可以提取的结构化数据时，在回答末尾输出：

<extraction>
{
  "behavior_metrics": { ... },
  "rubric_scores": { ... },
  "extraction_confidence": "high|medium|low",
  "reasoning": "为什么提取了这些值"
}
</extraction>

规则：
- 只在有明确数据时输出 extraction block
- 不要猜测数值——如果用户没提到，不要填
- extraction_confidence 反映你对提取准确度的判断
- 如果用户说的模糊（"还行"、"一般"），confidence 应该是 low 或 medium
```

### Implementation Steps

1. 创建 `apps/api/src/alters_lab/schemas/calibration_conversation.py`
2. 创建 `apps/api/src/alters_lab/services/calibration_conversation.py`
3. 创建 `apps/api/src/alters_lab/api/calibration_conversation.py`
4. 在 `main.py` 注册 router
5. 实现 LLM extraction 解析（regex 找 `<extraction>` block，json.loads 解析）
6. 实现 draft storage（`alters/product/calibration_drafts/`）
7. 实现 draft confirm/reject（confirm 时写入 behavior_metrics + calibration scores）
8. 前端对话界面
9. 前端 draft 确认卡片
10. 测试

### Tests Needed

- Schema validation（draft, extract, conversation）
- Extraction parser（从 LLM 输出中提取 JSON）
- Draft lifecycle（create → confirm → write）
- Draft rejection
- Mock provider 模式下的完整对话流程
- Edge cases：空 extraction、无效 JSON、超出范围的数值

---

## Phase 2: External Evidence Capture

**目标：** 用户在对话中提到真实世界事件，LLM 自动识别并提取为 external evidence

### Scope

- 扩展 `CalibrationConversationService` 的 extraction 能力
- 在 system prompt 中添加 external evidence 的 schema 定义
- Draft 中添加 `external_evidence` 字段
- Confirm 时写入 `external_evidence` records

### Additional Schema

```python
class ExternalEvidenceExtract(BaseModel):
    """Single evidence item the LLM can extract from conversation."""
    domain: Literal["career_education", "financial", "health",
                     "relationship", "subjective_wellbeing"]
    evidence_type: Literal["milestone_completed", "exam_or_certification",
                           "job_or_market_feedback", "project_shipped",
                           "income_or_financial_change", "health_measurement",
                           "relationship_event", "user_or_customer_feedback", "other"]
    description: str  # required, non-empty
    objective_strength: Literal["weak", "moderate", "strong"]
    polarity: Literal["positive", "negative", "neutral", "mixed"]
    numeric_value: float | None = None
    unit: str | None = None
```

### System Prompt Additions

```
3. External Evidence（外部证据）：
   当用户提到真实世界发生的事情时，提取为 external evidence：
   - 通过了考试/认证 → evidence_type: exam_or_certification
   - 完成了项目/里程碑 → evidence_type: milestone_completed
   - 收到了工作反馈 → evidence_type: job_or_market_feedback
   - 收入/财务变化 → evidence_type: income_or_financial_change
   - 健康测量数据 → evidence_type: health_measurement
   - 关系事件 → evidence_type: relationship_event

   判断 strength:
   - strong: 有明确数字或官方认证
   - moderate: 有具体事件但没有精确数据
   - weak: 主观感受或模糊描述
```

### Implementation Steps

1. 扩展 `CalibrationDraft` schema，添加 `external_evidence: list[ExternalEvidenceExtract]`
2. 更新 system prompt，添加 evidence extraction 指引
3. 更新 draft confirm 逻辑，写入 external_evidence records
4. 更新前端 draft 卡片，展示 evidence 条目
5. 测试

---

## Phase 3: Frontend Conversation UI + Draft Confirmation

**目标：** 在前端实现完整的对话界面和 draft 确认流程

### Scope

- 新页面或现有页面扩展：`CalibrationConversation`
- 对话界面（类似 Alter Dialogue，但针对 calibration）
- Draft 确认卡片（展示 LLM 提取的结构化数据）
- 用户可以编辑/纠正 draft 中的值
- 确认/拒绝按钮

### UI Design

```
┌─────────────────────────────────────────────────────────┐
│  Calibration Conversation                    [branch_A] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  LLM: 嗨！新的一周开始了。你这周怎么样？                    │
│                                                         │
│  User: 还行，每天大概学了两小时 Python，                    │
│        sleep 还不错，但是 exercise 基本没动。               │
│                                                         │
│  LLM: 收到。deep work 保持在 2 小时左右，                   │
│        sleep 看起来比较稳定。exercise 没动——                │
│        是身体原因还是时间安排？                             │
│                                                         │
│  ... (对话继续)                                          │
│                                                         │
│  ┌─ Draft ──────────────────────────────────────────┐   │
│  │  Behavior Metrics (Week of May 25)               │   │
│  │  Deep work: 120 min  [编辑]                       │   │
│  │  Sleep: 5 nights    [编辑]                        │   │
│  │  Exercise: 0 min    [编辑]                        │   │
│  │  Follow-through: 0.75 [编辑]                      │   │
│  │                                                  │   │
│  │  Rubric Scores                                   │   │
│  │  Execution: 3/5  [编辑]                           │   │
│  │  Energy: 2/5     [编辑]                           │   │
│  │                                                  │   │
│  │  External Evidence                               │   │
│  │  (none this conversation)                        │   │
│  │                                                  │   │
│  │  [确认写入]  [拒绝]  [继续对话]                     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  [输入消息...]                              [发送]        │
└─────────────────────────────────────────────────────────┘
```

### Implementation Steps

1. 新建 `apps/web/src/pages/CalibrationConversation.tsx`
2. 在 `App.tsx` 添加路由 `#calibration`
3. 在 `Sidebar` 添加导航入口
4. 实现对话界面（复用 AlterDialogue 的消息展示模式）
5. 实现 draft 确认卡片（可编辑字段 + 确认/拒绝按钮）
6. 在 `useApi.ts` 添加相关 hooks
7. 在 `api.ts` 添加 API 调用函数
8. i18n（en.json + zh.json 添加翻译）
9. 测试

---

## Phase 4: Expand to Outcome Targets + Predictor Profile

**目标：** 扩展 LLM 引导能力到低频数据类型

### Scope

- Outcome targets：LLM 引导用户定义可测量的目标
- Predictor profile：LLM 引导用户描述自己的 trait baseline 和 current context
- 这两个数据类型频率低，但对新用户的价值很大

### System Prompt Additions

```
4. Outcome Targets（结果目标）：
   当用户谈论未来目标或计划时，帮助他们定义可测量的 outcome target：
   - domain: 属于哪个生活领域
   - outcome_name: 目标名称
   - objective_definition: 客观定义（怎样算达成）
   - success_threshold: 成功阈值
   - measurement_method: 怎么测量

5. Predictor Profile（预测者画像）：
   当用户描述自己的性格、处境时，提取为 trait baseline 和 current context：
   - Big Five traits (0.0-1.0)
   - education/employment/financial/relationship status
   - health constraints
```

### Implementation Steps

1. 扩展 `CalibrationDraft` schema，添加 outcome_targets 和 predictor_profile 字段
2. 更新 system prompt
3. 更新 draft confirm 逻辑
4. 测试

---

## Technical Notes

### LLM Extraction Parser

```python
import re
import json

def extract_llm_data(llm_output: str) -> dict | None:
    """Extract structured data from LLM output using <extraction> tags."""
    match = re.search(r'<extraction>\s*(\{.*?\})\s*</extraction>',
                       llm_output, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
```

### Draft Storage

```
alters/product/calibration_drafts/
  cd_20260604T120000Z_abc123.yaml
  cd_20260604T130000Z_def456.yaml
```

### Conversation State Management

对话状态不需要持久化——每次 message 请求时，从 draft 和 conversation history 重建上下文。Conversation history 存在 `alters/product/calibration_conversations/` 下。

### Provider Mode Handling

- `mock` mode：LLM 返回预设的 extraction block，用于测试
- `disabled` mode：返回 "provider disabled" 消息
- `openai-compatible-http` mode：真实 LLM 调用

### Backward Compatibility

- 不修改任何现有 schema 或 service
- Draft confirm 写入的是现有的 `behavior_metrics/weekly_records` 和 `calibration/scores` 路径
- 现有的手动填写流程不受影响——LLM 引导是可选的增强路径

---

## Files to Create

| Phase | File | Type |
|-------|------|------|
| 1 | `apps/api/src/alters_lab/schemas/calibration_conversation.py` | Schema |
| 1 | `apps/api/src/alters_lab/services/calibration_conversation.py` | Service |
| 1 | `apps/api/src/alters_lab/api/calibration_conversation.py` | Router |
| 1 | `apps/api/tests/test_calibration_conversation.py` | Tests |
| 3 | `apps/web/src/pages/CalibrationConversation.tsx` | Page |
| 3 | `apps/web/src/pages/CalibrationConversation.test.tsx` | Tests |

## Files to Modify

| Phase | File | Change |
|-------|------|--------|
| 1 | `apps/api/src/alters_lab/main.py` | Register new router |
| 3 | `apps/web/src/App.tsx` | Add route |
| 3 | `apps/web/src/components/Sidebar.tsx` | Add nav entry |
| 3 | `apps/web/src/hooks/useApi.ts` | Add hooks |
| 3 | `apps/web/src/api.ts` | Add API functions |
| 3 | `apps/web/src/locales/en.json` | Add translations |
| 3 | `apps/web/src/locales/zh.json` | Add translations |
| 4 | `docs/architecture.md` | Update architecture |
| 4 | `docs/data-model.md` | Update data model |
