from __future__ import annotations

from pathlib import Path

from app.core.config import Settings
from app.db.chat_models import PestDiagnosisCase
from app.repositories.chat_repository import ChatRepository


class PestDiagnosisService:
    def __init__(self, repository: ChatRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def diagnose(self, *, attachment, conversation_id=None, message_id=None) -> dict:
        filename = (attachment.filename or "").lower()
        suffix = Path(filename).suffix.lower()

        label = "General crop stress"
        confidence = 0.42
        advice = "Inspect the crop closely for pest pressure, fungal lesions, and moisture stress."

        if any(token in filename for token in ["aphid", "mite", "thrip"]):
            label = "Likely insect pressure"
            confidence = 0.71
            advice = "Scout underside leaf surfaces, confirm pest density, and act quickly if the threshold is crossed."
        elif any(token in filename for token in ["rust", "blight", "fung", "mildew"]) or suffix in {".png", ".jpg", ".jpeg"}:
            label = "Possible fungal disease"
            confidence = 0.58
            advice = "Check lesion shape, humidity history, and canopy airflow. Reduce leaf wetness and confirm before treatment."

        case = PestDiagnosisCase(
            conversation_id=conversation_id,
            message_id=message_id,
            attachment_id=attachment.id,
            classifier_label=label,
            classifier_confidence=confidence,
            fallback_label=None,
            fallback_confidence=None,
            recommended_action=advice,
            metadata_json={
                "filename": attachment.filename,
                "mimeType": attachment.mime_type,
                "llmConfigured": bool(self.settings.deepseek_api_key or self.settings.gemini_api_key),
                "deepseekConfigured": bool(self.settings.deepseek_api_key),
                "geminiConfigured": bool(self.settings.gemini_api_key),
            },
        )
        self.repository.create_pest_case(case)

        return {
            "label": label,
            "confidence": confidence,
            "summary": f"{label}. {advice}",
            "recommendations": [
                advice,
                "Capture a second close-up image if symptoms are changing rapidly.",
                "Cross-check with local agronomic guidance before applying any treatment.",
            ],
        }
