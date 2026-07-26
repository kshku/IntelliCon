from __future__ import annotations

import logging
import os
import tempfile
import uuid
from datetime import UTC, datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.tools.base import ToolResult

logger = logging.getLogger(__name__)

PDF_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "intellicon_pdfs")
PDF_TTL_HOURS = 24


def _cleanup_old_pdfs() -> None:
    if not os.path.exists(PDF_OUTPUT_DIR):
        return
    now = datetime.now().timestamp()
    for fname in os.listdir(PDF_OUTPUT_DIR):
        fpath = os.path.join(PDF_OUTPUT_DIR, fname)
        try:
            age_hours = (now - os.path.getmtime(fpath)) / 3600
            if age_hours > PDF_TTL_HOURS:
                os.remove(fpath)
                logger.info("Cleaned up old PDF: %s", fname)
        except OSError:
            pass


def _format_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", str(item)))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content) if content else ""


class PdfExportTool:
    name = "pdf_export"
    description = (
        "Exports a conversation session as a formatted PDF document. "
        "Generates a downloadable report with messages, tool results, "
        "and metadata for case files and investigation reports."
    )
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The session ID to export as PDF",
            },
            "title": {
                "type": "string",
                "description": ("Optional title for the report (default: 'Investigation Report')"),
            },
        },
        "required": ["session_id"],
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        session_id = kwargs.get("session_id", "")
        if not session_id:
            return ToolResult(success=False, error="session_id is required")

        title = kwargs.get("title", "Investigation Report")

        try:
            from app.agent.session import SessionManager
            from app.config import settings

            manager = SessionManager(settings.REDIS_URL)
            state = await manager.load_session(session_id)
            await manager.close()
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Failed to load session: {exc}",
            )

        if state is None:
            return ToolResult(
                success=False,
                error=f"Session '{session_id}' not found or expired",
            )

        messages = state.get("messages", [])
        if not messages:
            return ToolResult(
                success=False,
                error="Session has no messages to export",
            )

        try:
            pdf_path = self._generate_pdf(
                session_id=session_id,
                title=title,
                messages=messages,
                context=state.get("context", {}),
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"PDF generation failed: {exc}",
            )

        filename = os.path.basename(pdf_path)
        download_url = f"/api/pdf/{filename}"

        return ToolResult(
            success=True,
            data=f"PDF exported successfully. Download: {download_url}",
            metadata={
                "pdf_path": pdf_path,
                "download_url": download_url,
                "filename": filename,
                "message_count": len(messages),
                "session_id": session_id,
            },
        )

    def _generate_pdf(
        self,
        session_id: str,
        title: str,
        messages: list,
        context: dict,
    ) -> str:
        _cleanup_old_pdfs()
        os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

        filename = f"intellicon_{session_id}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(PDF_OUTPUT_DIR, filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=6,
            textColor=colors.HexColor("#1a237e"),
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor("#283593"),
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=6,
        )
        code_style = ParagraphStyle(
            "Code",
            parent=styles["Code"],
            fontSize=8,
            leading=10,
            backColor=colors.HexColor("#f5f5f5"),
            borderColor=colors.HexColor("#e0e0e0"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=6,
        )
        meta_style = ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            spaceAfter=4,
        )

        story.append(Paragraph(f"IntelliCon — {title}", title_style))
        story.append(Spacer(1, 0.2 * cm))

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        meta_lines = [
            f"Generated: {now}",
            f"Session ID: {session_id}",
            f"Total Messages: {len(messages)}",
        ]
        if context.get("user_id"):
            meta_lines.append(f"User ID: {context['user_id']}")
        for line in meta_lines:
            story.append(Paragraph(line, meta_style))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Conversation History", heading_style))
        story.append(Spacer(1, 0.2 * cm))

        msg_num = 0
        for msg in messages:
            msg_type = getattr(msg, "type", "unknown")
            content = _format_message_content(getattr(msg, "content", ""))
            if not content:
                continue

            msg_num += 1

            if msg_type == "human":
                label = f"Q{msg_num}"
                label_color = "#1565c0"
            elif msg_type == "ai":
                label = f"A{msg_num}"
                label_color = "#2e7d32"
            elif msg_type == "tool":
                label = "Tool Result"
                label_color = "#e65100"
            else:
                label = msg_type.title()
                label_color = "#555555"

            msg_style = ParagraphStyle(
                f"Msg{msg_num}",
                parent=body_style,
                fontSize=10,
            )

            header = Paragraph(
                f'<font color="{label_color}"><b>[{label}]</b></font>',
                msg_style,
            )
            story.append(header)

            if msg_type == "ai":
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            tc_name = tc.get("name", "unknown")
                        else:
                            tc_name = getattr(tc, "name", "unknown")
                        story.append(
                            Paragraph(
                                f'<font color="#e65100">Tool Call: <b>{tc_name}</b></font>',
                                msg_style,
                            )
                        )

            if msg_type == "tool":
                story.append(Paragraph(content, code_style))
            else:
                safe = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(safe, msg_style))

            story.append(Spacer(1, 0.3 * cm))

        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("Audit Trail", heading_style))
        story.append(Spacer(1, 0.2 * cm))

        audit_data = [
            ["#", "Type", "Summary"],
        ]
        step_num = 0
        for msg in messages:
            msg_type = getattr(msg, "type", "unknown")
            content = _format_message_content(getattr(msg, "content", ""))
            if not content:
                continue
            step_num += 1
            summary = content[:80] + ("..." if len(content) > 80 else "")
            safe_summary = summary.replace("&", "&amp;").replace("<", "&lt;")
            audit_data.append(
                [
                    str(step_num),
                    msg_type.title(),
                    safe_summary,
                ]
            )

        if len(audit_data) > 1:
            audit_table = Table(
                audit_data,
                colWidths=[1 * cm, 2.5 * cm, 13 * cm],
            )
            audit_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eaf6")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#fafafa")],
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(audit_table)
        else:
            story.append(Paragraph("No audit data available.", meta_style))

        story.append(Spacer(1, 1 * cm))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#999999"),
            alignment=1,
        )
        story.append(
            Paragraph(
                "Generated by IntelliCon — Karnataka State Police Crime Database",
                footer_style,
            )
        )

        doc.build(story)
        logger.info("PDF generated: %s", pdf_path)
        return pdf_path
