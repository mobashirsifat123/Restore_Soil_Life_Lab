from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from urllib import parse, request
from uuid import UUID

from app.db.chat_models import ChatAnalysisSession, ChatToolRun, MarketPriceCache, WeatherCache
from app.domain.auth import AuthenticatedUser
from app.repositories.chat_repository import ChatRepository
from app.services.chat.knowledge_base_service import KnowledgeBaseService
from app.services.chat.pest_diagnosis_service import PestDiagnosisService
from app.services.chat.soil_chat_grounding_service import SoilChatGroundingService

ALLOWED_GUEST_TOOLS = {"knowledge_search", "weather", "market_prices", "pest_diagnosis"}


def score_to_band(score: float, score_bands: list[dict]) -> tuple[str, dict]:
    for band in score_bands:
        if float(band.get("min", 0)) <= score <= float(band.get("max", 100)):
            return str(band.get("label", "Functional")), band
    return "Functional", {}


def normalize_indicator_score(value: float, optimal_min: float, optimal_max: float) -> float:
    if optimal_min <= value <= optimal_max:
        return 100.0
    if value < optimal_min:
        span = max(optimal_min, 1.0)
        penalty = ((optimal_min - value) / span) * 100
    else:
        span = max(optimal_max, 1.0)
        penalty = ((value - optimal_max) / span) * 100
    return max(0.0, min(100.0, 100.0 - penalty))


class ToolRouterService:
    def __init__(
        self,
        repository: ChatRepository,
        knowledge_base_service: KnowledgeBaseService,
        pest_diagnosis_service: PestDiagnosisService,
        soil_grounding_service: SoilChatGroundingService,
    ) -> None:
        self.repository = repository
        self.knowledge_base_service = knowledge_base_service
        self.pest_diagnosis_service = pest_diagnosis_service
        self.soil_grounding_service = soil_grounding_service

    def detect_tool(self, content: str, *, tool_hint: str | None = None, quick_action: str | None = None, has_attachment: bool = False) -> str:
        if tool_hint:
            return tool_hint
        if quick_action:
            return quick_action

        lowered = content.lower()
        if has_attachment or any(keyword in lowered for keyword in ["photo", "leaf", "disease", "pest", "crop image"]):
            return "pest_diagnosis"
        if "weather" in lowered or "rain" in lowered or "forecast" in lowered:
            return "weather"
        if "market" in lowered or "price" in lowered or "mandi" in lowered:
            return "market_prices"
        if "last result" in lowered or "previous soil" in lowered or "history" in lowered:
            return "soil_history"
        if "compare" in lowered and ("formula" in lowered or "model" in lowered):
            return "formula_comparison"
        if "soil" in lowered or "microbe" in lowered or "fung" in lowered or "bacteria" in lowered:
            return "knowledge_search"
        return "knowledge_search"

    def route(
        self,
        *,
        tool_name: str,
        content: str,
        current_user: AuthenticatedUser | None,
        conversation_id: UUID | None,
        message_id: UUID | None,
        attachment=None,
        metadata: dict | None = None,
    ) -> dict:
        if current_user is None and tool_name not in ALLOWED_GUEST_TOOLS:
            return {
                "toolName": tool_name,
                "status": "sign_in_required",
                "confidence": 1.0,
                "summary": "Sign in to unlock personalized soil analysis and member history.",
                "recommendations": [
                    "Sign in to use soil analysis and result history.",
                    "Guests can still ask general farm, weather, market, and crop-photo questions.",
                ],
                "citations": [],
            }

        if tool_name == "soil_analysis":
            measurements = (metadata or {}).get("measurements") or {}
            return self.run_soil_analysis(
                inputs=measurements,
                current_user=current_user,
                conversation_id=conversation_id,
                message_id=message_id,
            )
        if tool_name == "soil_history":
            return self.run_soil_history(current_user=current_user)
        if tool_name == "formula_comparison":
            measurements = (metadata or {}).get("measurements") or {}
            return self.run_formula_comparison(
                inputs=measurements,
                current_user=current_user,
                conversation_id=conversation_id,
                message_id=message_id,
            )
        if tool_name == "weather":
            return self.run_weather(content=content)
        if tool_name == "market_prices":
            return self.run_market_prices(content=content)
        if tool_name == "pest_diagnosis":
            if attachment is None:
                return {
                    "toolName": "pest_diagnosis",
                    "status": "needs_attachment",
                    "confidence": 0.2,
                    "summary": "Upload a crop photo so I can inspect likely pest or disease pressure.",
                    "recommendations": ["Attach a close-up photo of the affected crop tissue."],
                    "citations": [],
                }
            return self.pest_diagnosis_service.diagnose(
                attachment=attachment,
                conversation_id=conversation_id,
                message_id=message_id,
            ) | {"toolName": "pest_diagnosis", "status": "succeeded"}

        return self.run_knowledge_search(content=content)

    def run_soil_history(self, *, current_user: AuthenticatedUser | None) -> dict:
        if current_user is None:
            return {
                "toolName": "soil_history",
                "status": "sign_in_required",
                "confidence": 1.0,
                "summary": "Sign in to access your saved soil analysis history.",
                "recommendations": ["Use a member account to store and revisit previous analyses."],
                "citations": [],
            }

        latest = self.soil_grounding_service.get_latest_member_analysis(current_user.user_id)
        if latest is None:
            return {
                "toolName": "soil_history",
                "status": "empty",
                "confidence": 0.6,
                "summary": "I could not find a saved soil analysis yet. Run a soil analysis first and I’ll explain it here.",
                "recommendations": ["Use the Analyze my soil action to create your first saved analysis."],
                "citations": [],
            }

        return {
            "toolName": "soil_history",
            "status": "succeeded",
            "confidence": 0.82,
            "summary": latest["summary"],
            "recommendations": list(latest["result"].get("recommendations", []))[:3],
            "citations": [
                {
                    "title": latest["formulaName"] or "Active SilkSoil formula",
                    "sourceType": "calculator_formula",
                    "snippet": latest["summary"],
                    "sourceUrl": None,
                }
            ],
            "result": latest["result"],
        }

    def run_knowledge_search(self, *, content: str) -> dict:
        results = self.knowledge_base_service.search(content)
        if not results:
            return {
                "toolName": "knowledge_search",
                "status": "empty",
                "confidence": 0.35,
                "summary": "I do not have a grounded answer yet from the current Bio Soil knowledge base. Try asking with more soil or crop detail.",
                "recommendations": [
                    "Mention the crop, soil issue, region, or management goal.",
                    "Upload a crop photo if you want pest or disease help.",
                ],
                "citations": [],
            }

        top = results[0]
        return {
            "toolName": "knowledge_search",
            "status": "succeeded",
            "confidence": 0.74,
            "summary": top["snippet"],
            "recommendations": [
                "Ask a follow-up question if you want this turned into a step-by-step recommendation.",
            ],
            "citations": [
                {
                    "title": item["title"],
                    "sourceType": item["source_type"],
                    "snippet": item["snippet"],
                    "sourceUrl": item["source_url"],
                }
                for item in results
            ],
        }

    def _calculate_score_for_formula(self, inputs: dict, formula_json: dict) -> dict:
        weights = formula_json.get("weights") or {}
        score_bands = formula_json.get("score_bands") or [
            {"min": 0, "max": 39, "label": "Severely constrained"},
            {"min": 40, "max": 59, "label": "Recovering"},
            {"min": 60, "max": 74, "label": "Functional"},
            {"min": 75, "max": 89, "label": "Strong"},
            {"min": 90, "max": 100, "label": "Highly resilient"},
        ]

        bacteria = float(inputs.get("bacteria", 0))
        fungi = float(inputs.get("fungi", 0))
        protozoa = float(inputs.get("protozoa", 0))
        nematodes = float(inputs.get("nematodes", 0))
        microbial_activity = max(0.0, min(100.0, ((bacteria + fungi + protozoa * 8 + nematodes * 0.5) / 4.0)))
        ratio = fungi / max(bacteria, 1.0)

        aliases = {
            "ph": float(inputs.get("ph", 0)),
            "organic_matter": float(inputs.get("organicMatter", 0)),
            "moisture": float(inputs.get("moisture", 0)),
            "temperature": float(inputs.get("temperature", 0)),
            "microbial_activity": microbial_activity,
            "fungal_bacterial_ratio": ratio,
        }

        component_scores: dict[str, float] = {}
        total = 0.0
        total_weight = 0.0
        for key, config in weights.items():
            if key not in aliases:
                continue
            weight = float(config.get("weight", 0))
            component_score = normalize_indicator_score(
                aliases[key],
                float(config.get("optimal_min", aliases[key])),
                float(config.get("optimal_max", aliases[key])),
            )
            component_scores[key] = round(component_score, 1)
            total += component_score * weight
            total_weight += weight

        score = round(total / total_weight if total_weight else 0.0, 1)
        band, band_meta = score_to_band(score, score_bands)
        
        return {
            "score": score,
            "band": band,
            "bandMeta": band_meta,
            "componentScores": component_scores,
            "microbialActivity": microbial_activity,
            "fungalBacterialRatio": ratio,
        }

    def run_formula_comparison(
        self,
        *,
        inputs: dict,
        current_user: AuthenticatedUser | None,
        conversation_id: UUID | None,
        message_id: UUID | None,
    ) -> dict:
        required = ["ph", "organicMatter", "moisture", "temperature", "bacteria", "fungi"]
        if not all(key in inputs for key in required):
            return {
                "toolName": "formula_comparison",
                "status": "needs_inputs",
                "confidence": 0.4,
                "summary": "I need pH, organic matter, moisture, temperature, bacteria, and fungi values to compare formulas.",
                "recommendations": ["Provide the missing measurements and try again."],
                "citations": [],
            }

        active_formulas = self.soil_grounding_service.get_all_active_formulas()
        if len(active_formulas) < 2:
            return {
                "toolName": "formula_comparison",
                "status": "not_enough_formulas",
                "confidence": 1.0,
                "summary": "There are not enough active formulas to compare. Ask an admin to enable more formulas.",
                "recommendations": ["Use standard soil analysis instead."],
                "citations": [],
            }

        comparisons = []
        for formula in active_formulas:
            calc_result = self._calculate_score_for_formula(inputs, formula.formula_json)
            comparisons.append({
                "formulaId": str(formula.id),
                "formulaName": formula.name,
                "score": calc_result["score"],
                "band": calc_result["band"],
            })

        summary = "Here is how your soil scores across different active formulas:\n"
        for comp in comparisons:
            summary += f"- {comp['formulaName']}: {comp['score']}/100 ({comp['band']})\n"

        result = {
            "toolName": "formula_comparison",
            "status": "succeeded",
            "confidence": 0.9,
            "summary": summary.strip(),
            "comparisons": comparisons,
            "recommendations": ["Review the differences in scoring based on different research models."],
            "citations": [],
        }

        self.repository.create_tool_run(
            ChatToolRun(
                conversation_id=conversation_id,
                message_id=message_id,
                tool_name="formula_comparison",
                status="succeeded",
                input_json=inputs,
                output_json=result,
                confidence=0.9,
                duration_ms=45,
            )
        )
        return result

    def run_soil_analysis(
        self,
        *,
        inputs: dict,
        current_user: AuthenticatedUser | None,
        conversation_id: UUID | None,
        message_id: UUID | None,
    ) -> dict:
        required = ["ph", "organicMatter", "moisture", "temperature", "bacteria", "fungi"]
        if not all(key in inputs for key in required):
            return {
                "toolName": "soil_analysis",
                "status": "needs_inputs",
                "confidence": 0.4,
                "summary": "I need pH, organic matter, moisture, temperature, bacteria, and fungi values to run the soil analysis.",
                "recommendations": [
                    "Provide the missing measurements and try again.",
                ],
                "citations": [],
            }

        formula = self.soil_grounding_service.get_active_formula()
        formula_json = formula.formula_json if formula else {}
        weights = formula_json.get("weights") or {}
        score_bands = formula_json.get("score_bands") or [
            {"min": 0, "max": 39, "label": "Severely constrained"},
            {"min": 40, "max": 59, "label": "Recovering"},
            {"min": 60, "max": 74, "label": "Functional"},
            {"min": 75, "max": 89, "label": "Strong"},
            {"min": 90, "max": 100, "label": "Highly resilient"},
        ]

        bacteria = float(inputs.get("bacteria", 0))
        fungi = float(inputs.get("fungi", 0))
        protozoa = float(inputs.get("protozoa", 0))
        nematodes = float(inputs.get("nematodes", 0))
        microbial_activity = max(0.0, min(100.0, ((bacteria + fungi + protozoa * 8 + nematodes * 0.5) / 4.0)))
        ratio = fungi / max(bacteria, 1.0)

        aliases = {
            "ph": float(inputs.get("ph", 0)),
            "organic_matter": float(inputs.get("organicMatter", 0)),
            "moisture": float(inputs.get("moisture", 0)),
            "temperature": float(inputs.get("temperature", 0)),
            "microbial_activity": microbial_activity,
            "fungal_bacterial_ratio": ratio,
        }

        component_scores: dict[str, float] = {}
        total = 0.0
        total_weight = 0.0
        for key, config in weights.items():
            if key not in aliases:
                continue
            weight = float(config.get("weight", 0))
            component_score = normalize_indicator_score(
                aliases[key],
                float(config.get("optimal_min", aliases[key])),
                float(config.get("optimal_max", aliases[key])),
            )
            component_scores[key] = round(component_score, 1)
            total += component_score * weight
            total_weight += weight

        score = round(total / total_weight if total_weight else 0.0, 1)
        band, band_meta = score_to_band(score, score_bands)

        recommendations: list[str] = []
        if component_scores.get("organic_matter", 100) < 60:
            recommendations.append("Increase organic residues or compost inputs to improve habitat for the soil food web.")
        if component_scores.get("fungal_bacterial_ratio", 100) < 60:
            recommendations.append("Reduce disturbance and support fungal recovery with mulch, roots, and reduced tillage.")
        if component_scores.get("moisture", 100) < 60:
            recommendations.append("Stabilize moisture with mulches, cover, and irrigation timing that avoids long dry gaps.")
        if component_scores.get("temperature", 100) < 60:
            recommendations.append("Protect soil from heat stress with cover and residue to keep biology active.")
        if component_scores.get("microbial_activity", 100) < 60:
            recommendations.append("Support microbial abundance with carbon inputs, living roots, and fewer disruptive inputs.")
        if not recommendations:
            recommendations.append("Maintain current biological momentum and keep monitoring seasonal changes.")

        summary = (
            f"Soil score {score}/100 — {band}. "
            f"Microbial activity is estimated at {round(microbial_activity, 1)} and the fungal:bacterial ratio is {ratio:.2f}."
        )

        result = {
            "toolName": "soil_analysis",
            "status": "succeeded",
            "confidence": 0.81,
            "summary": summary,
            "score": score,
            "band": band,
            "bandMeta": band_meta,
            "formulaName": formula.name if formula else None,
            "recommendations": recommendations,
            "componentScores": component_scores,
            "citations": [
                {
                    "title": formula.name if formula else "Active SilkSoil formula",
                    "sourceType": "calculator_formula",
                    "snippet": summary,
                    "sourceUrl": None,
                }
            ],
        }

        if current_user is not None:
            analysis = ChatAnalysisSession(
                organization_id=current_user.organization_id,
                user_id=current_user.user_id,
                formula_id=formula.id if formula else None,
                formula_name=formula.name if formula else None,
                input_json=inputs,
                result_json=result,
                summary=summary,
            )
            self.repository.save_analysis_session(analysis)

        self.repository.create_tool_run(
            ChatToolRun(
                conversation_id=conversation_id,
                message_id=message_id,
                tool_name="soil_analysis",
                status="succeeded",
                input_json=inputs,
                output_json=result,
                confidence=0.81,
                duration_ms=34,
            )
        )
        return result

    def _extract_location(self, content: str) -> str | None:
        match = re.search(r"(?:in|for|at)\s+([A-Za-z][A-Za-z\s,-]{2,})", content, re.IGNORECASE)
        if match:
            return match.group(1).strip(" ?.")
        return None

    def run_weather(self, *, content: str) -> dict:
        location = self._extract_location(content)
        if not location:
            return {
                "toolName": "weather",
                "status": "needs_location",
                "confidence": 0.3,
                "summary": "Tell me the city or village so I can give weather-aware advice.",
                "recommendations": ["Example: 'Weather advice for Nairobi'."],
                "citations": [],
            }

        key = location.lower()
        cached = self.repository.get_weather_cache(key)
        if cached and cached.expires_at and cached.expires_at > datetime.now(UTC):
            forecast = cached.forecast_json
            summary = cached.advisory_text or forecast.get("summary", "")
            return {
                "toolName": "weather",
                "status": "succeeded",
                "confidence": 0.76,
                "summary": summary,
                "forecast": forecast,
                "recommendations": forecast.get("recommendations", []),
                "citations": [{"title": f"Weather for {cached.normalized_location}", "sourceType": "weather_cache", "snippet": summary, "sourceUrl": None}],
            }

        try:
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search?" + parse.urlencode({"name": location, "count": 1})
            geocode = json.loads(request.urlopen(geocode_url, timeout=12).read().decode("utf-8"))
            results = geocode.get("results") or []
            if not results:
                raise ValueError("Location not found")
            match = results[0]
            forecast_url = "https://api.open-meteo.com/v1/forecast?" + parse.urlencode(
                {
                    "latitude": match["latitude"],
                    "longitude": match["longitude"],
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "forecast_days": 3,
                    "timezone": "auto",
                }
            )
            forecast_data = json.loads(request.urlopen(forecast_url, timeout=12).read().decode("utf-8"))
            daily = forecast_data.get("daily") or {}
            max_temp = (daily.get("temperature_2m_max") or [None])[0]
            min_temp = (daily.get("temperature_2m_min") or [None])[0]
            rainfall = (daily.get("precipitation_sum") or [0])[0]
            recommendations = []
            if rainfall and rainfall > 10:
                recommendations.append("Watch waterlogging risk and avoid compaction from field traffic after heavy rain.")
            else:
                recommendations.append("Use mulch and moisture monitoring to protect biological activity if rainfall stays light.")
            recommendations.append("Adjust irrigation and field operations to protect living soil structure.")
            summary = f"{match['name']}: forecast high {max_temp}°C, low {min_temp}°C, expected rainfall {rainfall} mm. {recommendations[0]}"
            forecast = {
                "location": match["name"],
                "country": match.get("country"),
                "high": max_temp,
                "low": min_temp,
                "rainfallMm": rainfall,
                "recommendations": recommendations,
                "summary": summary,
            }
            self.repository.upsert_weather_cache(
                WeatherCache(
                    location_key=key,
                    normalized_location=match["name"],
                    forecast_json=forecast,
                    advisory_text=summary,
                    expires_at=datetime.now(UTC) + timedelta(hours=6),
                )
            )
            return {
                "toolName": "weather",
                "status": "succeeded",
                "confidence": 0.82,
                "summary": summary,
                "forecast": forecast,
                "recommendations": recommendations,
                "citations": [{"title": f"Open-Meteo · {match['name']}", "sourceType": "weather", "snippet": summary, "sourceUrl": "https://open-meteo.com/"}],
            }
        except Exception:
            return {
                "toolName": "weather",
                "status": "failed",
                "confidence": 0.2,
                "summary": "I could not fetch the live weather just now. Try again in a moment.",
                "recommendations": ["Retry the weather request with a city or village name."],
                "citations": [],
            }

    def run_market_prices(self, *, content: str) -> dict:
        lowered = content.lower()
        crop_match = re.search(r"(price|market|mandi).*(for|of)?\s*([a-z][a-z\s-]{2,})", lowered)
        crop = crop_match.group(3).strip(" ?.") if crop_match else "your crop"
        region = self._extract_location(content) or "your region"
        lookup_key = f"{crop.lower()}::{region.lower()}"
        cached = self.repository.get_market_cache(lookup_key)
        if cached and cached.expires_at and cached.expires_at > datetime.now(UTC):
            market = cached.market_json
            return {
                "toolName": "market_prices",
                "status": "succeeded",
                "confidence": 0.55,
                "summary": cached.advisory_text or market.get("summary", ""),
                "market": market,
                "recommendations": market.get("recommendations", []),
                "citations": [{"title": f"Market advisory · {cached.crop_name}", "sourceType": "market_cache", "snippet": cached.advisory_text or "", "sourceUrl": None}],
            }

        recommendations = [
            "Compare local buyer offers with regional reference markets before selling.",
            "Track moisture, grading, and transport timing because these can change realized value more than headline price.",
            "If you want live prices later, connect a dedicated mandi or market data feed in admin.",
        ]
        summary = f"I do not have a live {crop} price feed configured for {region} yet, but I can still help with a market-readiness plan and selling checklist."
        market = {
            "crop": crop.title(),
            "region": region,
            "availability": "advisory_only",
            "recommendations": recommendations,
            "summary": summary,
        }
        self.repository.upsert_market_cache(
            MarketPriceCache(
                lookup_key=lookup_key,
                crop_name=crop.title(),
                region=region,
                market_json=market,
                advisory_text=summary,
                expires_at=datetime.now(UTC) + timedelta(hours=3),
            )
        )
        return {
            "toolName": "market_prices",
            "status": "succeeded",
            "confidence": 0.45,
            "summary": summary,
            "market": market,
            "recommendations": recommendations,
            "citations": [{"title": "BioSilk market advisory", "sourceType": "market_advisory", "snippet": summary, "sourceUrl": None}],
        }
