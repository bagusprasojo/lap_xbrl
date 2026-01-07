from __future__ import annotations

from typing import Iterable

from django.db import transaction
from django.utils import timezone

from .models import Company, Context, Fact, Filing
from .parser import ParsedContext, ParsedFact, ParsedResult, XBRLParser


class UploadConflictError(Exception):
    pass


class UploadResult:
    def __init__(self, filing: Filing, fact_count: int, context_count: int) -> None:
        self.filing = filing
        self.fact_count = fact_count
        self.context_count = context_count


def ingest_xbrl(file_obj, overwrite: bool = False) -> UploadResult:
    parser = XBRLParser(file_obj)
    parsed = parser.parse()

    if not parsed.facts:
        raise ValueError("File XBRL tidak memiliki fakta keuangan yang dapat diproses.")

    ticker = (parsed.entity_code or parsed.ticker).upper()
    company, created = Company.objects.get_or_create(
        ticker=ticker,
        defaults={
            "name": parsed.entity_name or ticker,
            "entity_code": parsed.entity_code or ticker,
            "entity_name": parsed.entity_name or "",
            "entity_main_industry": parsed.entity_main_industry or "",
            "sector": parsed.sector or "",
            "subsector": parsed.subsector or "",
            "industry": parsed.industry or "",
            "subindustry": parsed.subindustry or "",
        },
    )
    if not created:
        updated_fields = {}
        if parsed.entity_code and parsed.entity_code != company.entity_code:
            updated_fields["entity_code"] = parsed.entity_code
        if parsed.entity_name and parsed.entity_name != company.entity_name:
            updated_fields["entity_name"] = parsed.entity_name
        if parsed.entity_name and parsed.entity_name != company.name:
            updated_fields["name"] = parsed.entity_name
        if parsed.entity_main_industry and parsed.entity_main_industry != company.entity_main_industry:
            updated_fields["entity_main_industry"] = parsed.entity_main_industry
        if parsed.sector and parsed.sector != company.sector:
            updated_fields["sector"] = parsed.sector
        if parsed.subsector and parsed.subsector != company.subsector:
            updated_fields["subsector"] = parsed.subsector
        if parsed.industry and parsed.industry != company.industry:
            updated_fields["industry"] = parsed.industry
        if parsed.subindustry and parsed.subindustry != company.subindustry:
            updated_fields["subindustry"] = parsed.subindustry
        if updated_fields:
            Company.objects.filter(pk=company.pk).update(**updated_fields)

    existing = (
        Filing.objects.filter(company=company, period_label=parsed.period_label)
        .select_related("company")
        .first()
    )
    if existing and not overwrite:
        raise UploadConflictError(
            "Laporan untuk emiten dan periode ini sudah ada. Aktifkan opsi timpa data."
        )

    with transaction.atomic():
        if existing:
            existing.delete()

        file_obj.seek(0)
        filing = Filing.objects.create(
            company=company,
            period_label=parsed.period_label,
            period_start=parsed.period_start,
            period_end=parsed.period_end,
            instant_date=parsed.instant_date,
            context_reference="",
            document_type="",
            source_filename=getattr(file_obj, "name", ""),
            xbrl_file=file_obj,
            uploaded_at=timezone.now(),
        )

        context_lookup = _persist_contexts(filing, parsed.contexts)
        fact_count = _persist_facts(filing, parsed.facts, context_lookup)

    return UploadResult(filing=filing, fact_count=fact_count, context_count=len(context_lookup))


def _persist_contexts(
    filing: Filing, parsed_contexts: Iterable[ParsedContext]
) -> dict[str, Context]:
    context_lookup: dict[str, Context] = {}
    for ctx in parsed_contexts:
        context = Context.objects.create(
            filing=filing,
            context_id=ctx.context_id,
            entity_identifier=ctx.entity_identifier or "",
            start_date=ctx.start_date,
            end_date=ctx.end_date,
            instant_date=ctx.instant_date,
            period_type=ctx.period_type,
        )
        context_lookup[ctx.context_id] = context
    return context_lookup


def _persist_facts(
    filing: Filing, parsed_facts: Iterable[ParsedFact], context_lookup: dict[str, Context]
) -> int:
    fact_objects = []
    for idx, fact in enumerate(parsed_facts):
        context = context_lookup.get(fact.context_ref or "")
        fact_objects.append(
            Fact(
                filing=filing,
                context=context,
                name=fact.name,
                namespace=fact.namespace,
                value=fact.value or "",
                unit=fact.unit_ref or "",
                decimals=fact.decimals or "",
                order=idx,
            )
        )
    Fact.objects.bulk_create(fact_objects, batch_size=500)
    return len(fact_objects)
