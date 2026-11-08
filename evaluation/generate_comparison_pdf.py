#!/usr/bin/env python3
"""Generate the comparison PDF and include the evaluation-mode limitations."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent


def _read_results(filename: str) -> dict[str, dict]:
    path = ROOT / filename
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"{filename} must contain a non-empty per-case result object.")
    return payload


def _execution_mode() -> str:
    report = (ROOT / "comparison.md").read_text(encoding="utf-8")
    for line in report.splitlines():
        if line.startswith("Execution mode: "):
            return line.removeprefix("Execution mode: ").rstrip(".")
    raise ValueError("comparison.md is missing its execution mode.")


def main() -> None:
    baseline = _read_results("baseline_results.json")
    agent = _read_results("agent_results.json")
    if baseline.keys() != agent.keys():
        raise ValueError("Baseline and agent results contain different cases.")

    case_names = sorted(baseline)
    if len(case_names) != 10:
        raise ValueError(f"Expected 10 named benchmark cases, found {len(case_names)}.")

    table_data = [[
        "Case",
        "Baseline accuracy",
        "Agent accuracy",
        "Delta",
        "FP (baseline)",
        "FP (agent)",
    ]]
    for case_name in case_names:
        base = baseline[case_name]
        candidate = agent[case_name]
        delta = candidate["evidence_accuracy"] - base["evidence_accuracy"]
        table_data.append([
            case_name,
            f"{base['evidence_accuracy']:.1f}%",
            f"{candidate['evidence_accuracy']:.1f}%",
            f"{delta:+.1f} pp",
            str(base["false_positives"]),
            str(candidate["false_positives"]),
        ])

    base_average = sum(baseline[name]["evidence_accuracy"] for name in case_names) / 10
    agent_average = sum(agent[name]["evidence_accuracy"] for name in case_names) / 10
    table_data.append([
        "Aggregate",
        f"{base_average:.1f}%",
        f"{agent_average:.1f}%",
        f"{agent_average - base_average:+.1f} pp",
        str(sum(baseline[name]["false_positives"] for name in case_names)),
        str(sum(agent[name]["false_positives"] for name in case_names)),
    ])

    mode = _execution_mode()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#183153"),
        alignment=0,
    )
    note_style = ParagraphStyle(
        "ReportNote",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        spaceAfter=4,
    )

    if "heuristic" in mode.lower() or "fallback" in mode.lower():
        limitation = (
            "Both systems use the same deterministic heuristic in this mode, so "
            "identical results are expected. The scores verify that the harness runs; "
            "they do not demonstrate an improvement from the agent. A Gemini-powered "
            "comparison is required to measure that."
        )
    else:
        limitation = (
            "These results describe one Gemini-powered run on the 10 labelled cases. "
            "They are not, on their own, statistical evidence of general performance."
        )

    table = Table(
        table_data,
        colWidths=[62 * mm, 34 * mm, 34 * mm, 28 * mm, 30 * mm, 30 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F1F5F9")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCE6F1")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C5D1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    output = ROOT / "ResumePilot AI comparison.pdf"
    document = SimpleDocTemplate(
        str(output),
        pagesize=landscape(A4),
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="ResumePilot AI evaluation comparison",
    )
    document.build([
        Paragraph("ResumePilot AI: Baseline vs. Agent", title_style),
        Spacer(1, 3 * mm),
        Paragraph(f"Execution mode: {mode}.", note_style),
        table,
        Spacer(1, 5 * mm),
        Paragraph("<b>Interpretation and limitations</b>", note_style),
        Paragraph(limitation, note_style),
    ])
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
