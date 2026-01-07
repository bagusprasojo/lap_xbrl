from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import IO
from xml.etree import ElementTree as ET

from django.core.files.uploadedfile import UploadedFile

XBRLI_NS = "http://www.xbrl.org/2003/instance"


@dataclass
class ParsedContext:
    context_id: str
    entity_identifier: str | None
    start_date: date | None
    end_date: date | None
    instant_date: date | None
    period_type: str


@dataclass
class ParsedFact:
    name: str
    namespace: str
    value: str | None
    context_ref: str | None
    unit_ref: str | None
    decimals: str | None


@dataclass
class ParsedResult:
    ticker: str
    entity_code: str | None
    entity_name: str | None
    entity_main_industry: str | None
    sector: str | None
    subsector: str | None
    industry: str | None
    subindustry: str | None
    period_label: str
    period_start: date | None
    period_end: date | None
    instant_date: date | None
    contexts: list[ParsedContext]
    facts: list[ParsedFact]


class XBRLParser:
    """Utility untuk membaca struktur dasar file XBRL."""

    def __init__(self, file_obj: UploadedFile | IO[bytes]):
        self.file_obj = file_obj

    def parse(self) -> ParsedResult:
        self.file_obj.seek(0)
        tree = ET.parse(self.file_obj)
        root = tree.getroot()

        contexts = self._parse_contexts(root)
        facts = self._parse_facts(root)

        ticker = self._guess_ticker(contexts)
        period_start, period_end, instant_date, period_label = self._guess_period(
            root, contexts
        )
        entity_code = self._find_fact_text(root, "EntityCode")
        entity_name = self._find_fact_text(root, "EntityName")
        entity_main_industry = self._find_fact_text(root, "EntityMainIndustry")
        sector = self._find_fact_text(root, "Sector")
        subsector = self._find_fact_text(root, "Subsector")
        industry = self._find_fact_text(root, "Industry")
        subindustry = self._find_fact_text(root, "Subindustry")

        return ParsedResult(
            ticker=ticker,
            entity_code=entity_code,
            entity_name=entity_name,
            entity_main_industry=entity_main_industry,
            sector=sector,
            subsector=subsector,
            industry=industry,
            subindustry=subindustry,
            period_label=period_label,
            period_start=period_start,
            period_end=period_end,
            instant_date=instant_date,
            contexts=contexts,
            facts=facts,
        )

    def _parse_contexts(self, root: ET.Element) -> list[ParsedContext]:
        contexts: list[ParsedContext] = []
        for ctx in root.findall(f".//{{{XBRLI_NS}}}context"):
            context_id = ctx.attrib.get("id")
            if not context_id:
                continue

            entity_identifier = None
            identifier_el = ctx.find(f"./{{{XBRLI_NS}}}entity/{{{XBRLI_NS}}}identifier")
            if identifier_el is not None and identifier_el.text:
                entity_identifier = identifier_el.text.strip()

            period_el = ctx.find(f"./{{{XBRLI_NS}}}period")
            start_date = end_date = instant_date = None
            period_type = "unknown"
            if period_el is not None:
                start_el = period_el.find(f"./{{{XBRLI_NS}}}startDate")
                end_el = period_el.find(f"./{{{XBRLI_NS}}}endDate")
                instant_el = period_el.find(f"./{{{XBRLI_NS}}}instant")
                if start_el is not None and end_el is not None:
                    start_date = self._parse_date(start_el.text)
                    end_date = self._parse_date(end_el.text)
                    period_type = "duration"
                elif instant_el is not None:
                    instant_date = self._parse_date(instant_el.text)
                    period_type = "instant"

            contexts.append(
                ParsedContext(
                    context_id=context_id,
                    entity_identifier=entity_identifier,
                    start_date=start_date,
                    end_date=end_date,
                    instant_date=instant_date,
                    period_type=period_type,
                )
            )
        return contexts

    def _parse_facts(self, root: ET.Element) -> list[ParsedFact]:
        facts: list[ParsedFact] = []
        for elem in root:
            if not isinstance(elem.tag, str):
                continue
            if elem.tag.startswith(f"{{{XBRLI_NS}}}") or "contextRef" not in elem.attrib:
                continue

            namespace, local_name = self._split_tag(elem.tag)
            value = elem.text.strip() if elem.text else None
            facts.append(
                ParsedFact(
                    name=local_name,
                    namespace=namespace,
                    value=value,
                    context_ref=elem.attrib.get("contextRef"),
                    unit_ref=elem.attrib.get("unitRef"),
                    decimals=elem.attrib.get("decimals"),
                )
            )
        return facts

    def _guess_ticker(self, contexts: list[ParsedContext]) -> str:
        for ctx in contexts:
            if ctx.entity_identifier:
                return ctx.entity_identifier.split(":")[-1].upper()
        return "UNKNOWN"

    def _guess_period(
        self, root: ET.Element, contexts: list[ParsedContext]
    ) -> tuple[date | None, date | None, date | None, str]:
        period_end = self._find_fact_date(root, "DocumentPeriodEndDate")
        period_start = self._find_fact_date(root, "DocumentPeriodStartDate")
        instant_date = self._find_fact_date(root, "DocumentPeriodInstantDate")

        if not period_end:
            for ctx in contexts:
                if ctx.period_type == "duration" and ctx.end_date:
                    period_end = ctx.end_date
                    period_start = ctx.start_date
                    break
        if not instant_date:
            for ctx in contexts:
                if ctx.period_type == "instant" and ctx.instant_date:
                    instant_date = ctx.instant_date
                    break

        period_label = ""
        if period_end:
            period_label = period_end.isoformat()
        elif instant_date:
            period_label = instant_date.isoformat()
        else:
            period_label = datetime.now().strftime("%Y-%m-%d")

        return period_start, period_end, instant_date, period_label

    def _find_fact_date(self, root: ET.Element, target_name: str) -> date | None:
        for elem in root.iter():
            if not isinstance(elem.tag, str):
                continue
            _, local_name = self._split_tag(elem.tag)
            if local_name == target_name and elem.text:
                return self._parse_date(elem.text)
        return None

    def _find_fact_text(self, root: ET.Element, target_name: str) -> str | None:
        for elem in root.iter():
            if not isinstance(elem.tag, str):
                continue
            _, local_name = self._split_tag(elem.tag)
            if local_name == target_name and elem.text:
                value = elem.text.strip()
                if value:
                    return value
        return None

    def _split_tag(self, tag: str) -> tuple[str, str]:
        if "}" in tag:
            namespace, local = tag[1:].split("}", 1)
            return namespace, local
        return "", tag

    def _parse_date(self, value: str | None) -> date | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None
