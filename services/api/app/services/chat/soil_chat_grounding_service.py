from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.cms import CalculatorFormula
from app.repositories.chat_repository import ChatRepository


class SoilChatGroundingService:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    def get_active_formula(self) -> CalculatorFormula | None:
        return self.repository.session.scalar(
            select(CalculatorFormula).where(CalculatorFormula.is_active.is_(True))
        )

    def get_all_active_formulas(self) -> list[CalculatorFormula]:
        return list(
            self.repository.session.scalars(
                select(CalculatorFormula).where(CalculatorFormula.is_active.is_(True))
            )
        )

    def get_latest_member_analysis(self, user_id: UUID) -> dict | None:
        latest = self.repository.get_latest_analysis_session(user_id)
        if latest is None:
            return None
        return {
            "formulaName": latest.formula_name,
            "summary": latest.summary,
            "result": latest.result_json,
            "inputs": latest.input_json,
            "createdAt": latest.created_at.isoformat(),
        }
