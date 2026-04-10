from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.db.chat_models import ChatKnowledgeChunk, ChatKnowledgeSource
from app.models.cms import BlogPost, CalculatorFormula, CmsPage, CmsSection
from app.repositories.chat_repository import ChatRepository


def chunk_text(value: str, *, size: int = 500) -> list[str]:
    text = " ".join(value.split())
    if not text:
        return []
    return [text[index : index + size] for index in range(0, len(text), size)]


class KnowledgeBaseService:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    def sync_system_sources(self) -> list[ChatKnowledgeSource]:
        session = self.repository.session
        existing = {item.title: item for item in self.repository.list_sources()}

        pages = list(session.query(CmsPage).all())
        sections = list(session.query(CmsSection).all())
        posts = list(session.query(BlogPost).all())
        formulas = list(session.query(CalculatorFormula).all())

        page_sections: dict[str, list[CmsSection]] = {}
        for section in sections:
            page_sections.setdefault(section.page_slug, []).append(section)

        system_payloads: list[tuple[str, str, str]] = []
        for page in pages:
            body_parts = [page.title, page.meta_description or "", page.hero_heading or "", page.hero_subheading or ""]
            for section in page_sections.get(page.slug, []):
                body_parts.append(f"{section.section_key}: {section.content_json}")
            system_payloads.append(("cms_page", f"CMS · {page.title}", "\n".join(part for part in body_parts if part)))

        if posts:
            body = "\n\n".join(
                f"{post.title}\n{post.excerpt or ''}\n{post.body_markdown or ''}" for post in posts
            )
            system_payloads.append(("blog_posts", "CMS · Blog Posts", body))

        if formulas:
            body = "\n\n".join(
                f"{formula.name}\nActive: {formula.is_active}\n{formula.formula_json}\n{formula.changelog or ''}"
                for formula in formulas
            )
            system_payloads.append(("calculator_formulas", "CMS · Calculator Formulas", body))

        synced: list[ChatKnowledgeSource] = []
        for source_type, title, body_text in system_payloads:
            source = existing.get(title)
            if source is None:
                source = ChatKnowledgeSource(
                    source_type=source_type,
                    title=title,
                    body_text=body_text,
                    is_enabled=True,
                    metadata_json={"systemManaged": True},
                )
                synced.append(self.repository.create_source(source))
                continue

            source.source_type = source_type
            source.body_text = body_text
            source.metadata_json = {**(source.metadata_json or {}), "systemManaged": True}
            source.updated_at = datetime.now(UTC)
            synced.append(self.repository.update_source(source))

        return synced

    def reindex_source(self, source_id: UUID) -> tuple[ChatKnowledgeSource, int]:
        source = self.repository.get_source(source_id)
        if source is None:
            raise ValueError("Knowledge source not found.")

        chunks = [
            ChatKnowledgeChunk(
                source_id=source.id,
                chunk_index=index,
                content=chunk,
                metadata_json={"title": source.title, "sourceType": source.source_type},
            )
            for index, chunk in enumerate(chunk_text(source.body_text or ""))
        ]
        count = self.repository.replace_source_chunks(source.id, chunks)
        source = self.repository.get_source(source_id)
        if source is None:
            raise ValueError("Knowledge source not found after reindex.")
        return source, count

    def sync_and_reindex_defaults(self) -> None:
        for source in self.sync_system_sources():
            self.reindex_source(source.id)

    def search(self, query_text: str, *, limit: int = 5) -> list[dict]:
        self.sync_system_sources()
        results = self.repository.search_chunks(query_text, limit=limit)
        return [
            {
                "title": source.title,
                "source_type": source.source_type,
                "source_url": source.source_url,
                "snippet": chunk.content[:260],
                "metadata": source.metadata_json or {},
            }
            for chunk, source in results
        ]
