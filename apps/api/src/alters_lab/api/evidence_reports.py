from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.evidence_reports import (
    ActiveYamlValidationSummary,
    Day30DemoSummary,
    EvidenceHealthResponse,
    EvidenceReportInfo,
    EvidenceReportsResponse,
    EvidenceStatusResponse,
    Phase1CloseoutSummary,
)
from alters_lab.services.evidence_reports import (
    build_evidence_status,
    evidence_paths,
    load_json_report,
    load_optional_text_metadata,
    summarize_active_yaml_validation,
    summarize_day30_demo,
)

router = APIRouter(prefix="/evidence", tags=["evidence-reports"])


@router.get("/health", response_model=EvidenceHealthResponse)
def health():
    return EvidenceHealthResponse()


@router.get("/status", response_model=EvidenceStatusResponse)
def status():
    raw = build_evidence_status()
    return EvidenceStatusResponse(
        day30_demo=Day30DemoSummary(**raw["day30_demo"]),
        active_yaml_validation=ActiveYamlValidationSummary(**raw["active_yaml_validation"]),
        phase1_closeout=Phase1CloseoutSummary(**raw["phase1_closeout"]),
    )


@router.get("/reports", response_model=EvidenceReportsResponse)
def reports():
    paths = evidence_paths()
    infos = []
    for key, path in paths.items():
        fmt = "json" if path.suffix == ".json" else "markdown"
        infos.append(EvidenceReportInfo(key=key, path=str(path), exists=path.exists(), format=fmt))
    return EvidenceReportsResponse(reports=infos, count=len(infos))


@router.get("/day30-demo", response_model=Day30DemoSummary)
def day30_demo():
    paths = evidence_paths()
    path = paths["day30_demo"]
    if not path.exists():
        return Day30DemoSummary(status="MISSING", exists=False)
    try:
        report = load_json_report(path)
    except Exception as exc:
        return Day30DemoSummary(status="ERROR", exists=True, error=str(exc))
    return Day30DemoSummary(status="ok", exists=True, **summarize_day30_demo(report))


@router.get("/active-yaml-validation", response_model=ActiveYamlValidationSummary)
def active_yaml_validation():
    paths = evidence_paths()
    path = paths["active_yaml_validation"]
    if not path.exists():
        return ActiveYamlValidationSummary(status="MISSING", exists=False)
    try:
        report = load_json_report(path)
    except Exception as exc:
        return ActiveYamlValidationSummary(status="ERROR", exists=True, error=str(exc))
    return ActiveYamlValidationSummary(status="ok", exists=True, **summarize_active_yaml_validation(report))


@router.get("/phase1-closeout", response_model=Phase1CloseoutSummary)
def phase1_closeout():
    paths = evidence_paths()
    path = paths["phase1_closeout"]
    if not path.exists():
        return Phase1CloseoutSummary(status="MISSING", exists=False)
    meta = load_optional_text_metadata(path)
    return Phase1CloseoutSummary(status="ok", **meta)
