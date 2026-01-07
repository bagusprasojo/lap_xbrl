from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View

from .forms import TemplateForm, TemplateItemForm, XBRLUploadForm
from .models import Company, Fact, Filing, ReportTemplate, TemplateItem
from .services import UploadConflictError, ingest_xbrl


class HomeView(View):
    template_name = "reports/public/index.html"

    def get(self, request):
        company_count = Company.objects.count()
        filing_count = Filing.objects.count()
        template_count = ReportTemplate.objects.count()
        return render(
            request,
            self.template_name,
            {
                "company_count": company_count,
                "filing_count": filing_count,
                "template_count": template_count,
            },
        )


class PublicReportView(View):
    template_name = "reports/public/report.html"
    report_slug: str | None = None

    def get(self, request):
        report_slug = (self.report_slug or "").strip().lower()
        report_template = _get_report_template(report_slug)
        companies = list(Company.objects.all())
        company_id = request.GET.get("company")
        primary_id = request.GET.get("primary")
        comparison_id = request.GET.get("comparison")

        selected_company = None
        if company_id:
            selected_company = next(
                (c for c in companies if str(c.id) == company_id), None
            )
        if not selected_company and companies:
            selected_company = companies[0]

        filings = []
        if selected_company:
            filings = list(
                Filing.objects.filter(company=selected_company).order_by("-uploaded_at")
            )

        primary_filing = _find_filing(filings, primary_id) or (filings[0] if filings else None)
        comparison_filing = _find_filing(filings, comparison_id)

        report_blocks = []
        primary_lookup = _fact_lookup(primary_filing) if primary_filing else {}
        comparison_lookup = _fact_lookup(comparison_filing) if comparison_filing else {}
        if primary_filing and report_template:
            rows = _build_template_rows(report_template, primary_lookup, comparison_lookup)
            report_blocks.append({"template": report_template, "rows": rows})

        context = {
            "companies": companies,
            "filings": filings,
            "selected_company": selected_company,
            "primary_filing": primary_filing,
            "comparison_filing": comparison_filing,
            "report_blocks": report_blocks,
            "report_template": report_template,
            "report_slug": report_slug,
            "report_title": _report_title(report_template, report_slug),
        }
        return render(request, self.template_name, context)


class CompanyListView(View):
    template_name = "reports/public/companies.html"

    def get(self, request):
        query = request.GET.get("q", "").strip()
        company_qs = Company.objects.all()
        if query:
            company_qs = company_qs.filter(
                models.Q(ticker__icontains=query) | models.Q(name__icontains=query)
            )

        paginator = Paginator(company_qs.order_by("ticker"), 12)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(
            request,
            self.template_name,
            {"page_obj": page_obj, "query": query},
        )


class UploadXBRLView(LoginRequiredMixin, View):
    template_name = "reports/dashboard/upload.html"
    success_url = reverse_lazy("upload_xbrl")

    def get(self, request):
        form = XBRLUploadForm()
        query = request.GET.get("q", "").strip()
        filings_qs = Filing.objects.select_related("company").order_by("-uploaded_at")
        if query:
            filings_qs = filings_qs.filter(
                models.Q(company__ticker__icontains=query)
                | models.Q(period_label__icontains=query)
                | models.Q(company__name__icontains=query)
            )
        paginator = Paginator(filings_qs, 10)
        page_number = request.GET.get("page")
        latest_filings = paginator.get_page(page_number)
        return render(
            request,
            self.template_name,
            {"form": form, "latest_filings": latest_filings, "query": query},
        )

    def post(self, request):
        form = XBRLUploadForm(request.POST, request.FILES)
        query = request.GET.get("q", "").strip()
        filings_qs = Filing.objects.select_related("company").order_by("-uploaded_at")
        if query:
            filings_qs = filings_qs.filter(
                models.Q(company__ticker__icontains=query)
                | models.Q(period_label__icontains=query)
                | models.Q(company__name__icontains=query)
            )
        paginator = Paginator(filings_qs, 10)
        page_number = request.GET.get("page")
        latest_filings = paginator.get_page(page_number)

        if form.is_valid():
            file_obj = form.cleaned_data["file"]
            overwrite = form.cleaned_data["overwrite"]
            try:
                result = ingest_xbrl(file_obj, overwrite=overwrite)
            except UploadConflictError as exc:
                form.add_error(None, str(exc))
            except Exception as exc:
                form.add_error(
                    None,
                    f"Gagal memproses file XBRL. Detail error: {exc}",
                )
            else:
                messages.success(
                    request,
                    f"Berhasil memproses {result.filing.company.ticker} "
                    f"periode {result.filing.period_label}. "
                    f"Fakta tersimpan: {result.fact_count}, konteks: {result.context_count}.",
                )
                return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"form": form, "latest_filings": latest_filings},
        )


class TemplateListView(LoginRequiredMixin, View):
    template_name = "reports/dashboard/templates_list.html"

    def get(self, request):
        templates = ReportTemplate.objects.order_by("name").all()
        return render(
            request,
            self.template_name,
            {"template_form": TemplateForm(), "templates": templates},
        )

    def post(self, request):
        action = request.POST.get("action")

        template_form = TemplateForm()

        if action == "create_template":
            template_form = TemplateForm(request.POST)
            if template_form.is_valid():
                template = template_form.save()
                messages.success(
                    request, f"Template {template.name} berhasil dibuat."
                )
                return redirect("manage_templates")
        elif action == "delete_template":
            template_id = request.POST.get("template_id")
            template = ReportTemplate.objects.filter(pk=template_id).first()
            if not template:
                messages.error(request, "Template tidak ditemukan.")
            else:
                template_name = template.name
                template.delete()
                messages.success(request, f"Template {template_name} beserta itemnya telah dihapus.")
                return redirect("manage_templates")

        return render(
            request,
            self.template_name,
            {
                "template_form": template_form,
                "templates": ReportTemplate.objects.order_by("name").all(),
            },
        )


class TemplateDetailView(LoginRequiredMixin, View):
    template_name = "reports/dashboard/template_detail.html"

    def get(self, request, template_id: int):
        template = get_object_or_404(ReportTemplate, pk=template_id)
        query = request.GET.get("q", "").strip()
        edit_item_id = request.GET.get("edit_item")
        editing_item = None
        item_form = TemplateItemForm(initial={"template": template})
        item_form.fields["template"].widget = forms.HiddenInput()
        if edit_item_id:
            editing_item = TemplateItem.objects.filter(
                pk=edit_item_id, template=template
            ).first()
            if editing_item:
                item_form = TemplateItemForm(instance=editing_item)
                item_form.fields["template"].widget = forms.HiddenInput()

        items_qs = template.items.order_by("order", "id")
        if query:
            items_qs = items_qs.filter(
                models.Q(label__icontains=query)
                | models.Q(primary_fact__icontains=query)
                | models.Q(fallback_facts__icontains=query)
            )
        paginator = Paginator(items_qs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(
            request,
            self.template_name,
            {
                "template": template,
                "item_form": item_form,
                "items": page_obj,
                "page_obj": page_obj,
                "query": query,
                "editing_item": editing_item,
            },
        )

    def post(self, request, template_id: int):
        template = get_object_or_404(ReportTemplate, pk=template_id)
        action = request.POST.get("action")
        editing_item = None

        form_data = request.POST.copy()
        form_data["template"] = str(template.id)
        item_form = TemplateItemForm(form_data)
        item_form.fields["template"].widget = forms.HiddenInput()

        if action == "create_item":
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.template = template
                item.save()
                messages.success(
                    request,
                    f"Item {item.label} berhasil ditambahkan ke {template.name}.",
                )
                return redirect("manage_template_detail", template_id=template.id)
        elif action == "update_item":
            item_id = request.POST.get("item_id")
            editing_item = TemplateItem.objects.filter(
                pk=item_id, template=template
            ).first()
            if not editing_item:
                messages.error(request, "Item tidak ditemukan.")
            else:
                form_data = request.POST.copy()
                form_data["template"] = str(template.id)
                item_form = TemplateItemForm(form_data, instance=editing_item)
                item_form.fields["template"].widget = forms.HiddenInput()
                if item_form.is_valid():
                    item = item_form.save(commit=False)
                    item.template = template
                    item.save()
                    messages.success(
                        request,
                        f"Item {item.label} pada {template.name} berhasil diperbarui.",
                    )
                    return redirect("manage_template_detail", template_id=template.id)
        elif action == "delete_item":
            item_id = request.POST.get("item_id")
            item = TemplateItem.objects.filter(pk=item_id, template=template).first()
            if not item:
                messages.error(request, "Item tidak ditemukan.")
            else:
                item_label = item.label
                item.delete()
                messages.success(
                    request,
                    f"Item {item_label} dari template {template.name} telah dihapus.",
                )
                return redirect("manage_template_detail", template_id=template.id)

        query = request.GET.get("q", "").strip()
        items_qs = template.items.order_by("order", "id")
        if query:
            items_qs = items_qs.filter(
                models.Q(label__icontains=query)
                | models.Q(primary_fact__icontains=query)
                | models.Q(fallback_facts__icontains=query)
            )
        paginator = Paginator(items_qs, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(
            request,
            self.template_name,
            {
                "template": template,
                "item_form": item_form,
                "items": page_obj,
                "page_obj": page_obj,
                "query": query,
                "editing_item": editing_item,
            },
        )


class FilingDetailView(LoginRequiredMixin, View):
    template_name = "reports/dashboard/filing_detail.html"

    def get(self, request, pk: int):
        filing = get_object_or_404(
            Filing.objects.select_related("company").prefetch_related("contexts"),
            pk=pk,
        )
        search_query = request.GET.get("q", "").strip()
        fact_qs = filing.facts.select_related("context").order_by("order", "id")
        if search_query:
            fact_qs = fact_qs.filter(
                models.Q(name__icontains=search_query) | models.Q(value__icontains=search_query)
            )

        paginator = Paginator(fact_qs, 25)
        page_number = request.GET.get("page")
        facts_page = paginator.get_page(page_number)

        return render(
            request,
            self.template_name,
            {
                "filing": filing,
                "facts_page": facts_page,
                "search_query": search_query,
            },
        )


class DeleteFilingView(LoginRequiredMixin, View):
    success_url = reverse_lazy("upload_xbrl")

    def post(self, request, pk: int):
        filing = Filing.objects.select_related("company").filter(pk=pk).first()
        if not filing:
            messages.error(request, "Filing tidak ditemukan.")
            return redirect(self.success_url)

        filing_label = filing.period_label or f"Filing {filing.pk}"
        company_ticker = filing.company.ticker
        xbrl_file = filing.xbrl_file
        filing.delete()
        if xbrl_file:
            xbrl_file.delete(save=False)
        messages.success(
            request,
            f"Filing {company_ticker} periode {filing_label} telah dihapus.",
        )
        return redirect(self.success_url)


def _find_filing(filings: list[Filing], filing_id: str | None):
    if not filing_id:
        return None
    for filing in filings:
        if str(filing.id) == filing_id:
            return filing
    return None


def _get_report_template(report_slug: str) -> ReportTemplate | None:
    if not report_slug:
        return None
    template = (
        ReportTemplate.objects.prefetch_related("items")
        .filter(slug=report_slug)
        .first()
    )
    if template:
        return template
    readable_name = report_slug.replace("-", " ").strip()
    return (
        ReportTemplate.objects.prefetch_related("items")
        .filter(name__icontains=readable_name)
        .first()
    )


def _report_title(report_template: ReportTemplate | None, report_slug: str) -> str:
    if report_template:
        return report_template.name
    fallback = report_slug.replace("-", " ").strip()
    if not fallback:
        return "Laporan"
    return fallback.title()


def _build_template_rows(
    template: ReportTemplate,
    primary_lookup: dict[str, Fact],
    comparison_lookup: dict[str, Fact],
) -> list[dict]:
    rows = []
    for item in template.items.all():
        primary_fact = _resolve_fact(primary_lookup, item)
        comparison_fact = _resolve_fact(comparison_lookup, item)
        row = {
            "label": item.label,
            "primary_fact": primary_fact,
            "comparison_fact": comparison_fact,
            "level": item.level,
        }
        row.update(_calculate_analysis(primary_fact, comparison_fact))
        rows.append(row)
    return rows


def _fact_lookup(filing: Filing | None) -> dict[str, Fact]:
    if not filing:
        return {}
    lookup: dict[str, Fact] = {}
    for fact in filing.facts.all():
        key = fact.name.lower()
        if key not in lookup:
            lookup[key] = fact
    return lookup


def _resolve_fact(fact_lookup: dict[str, Fact], item):
    codes = [item.primary_fact] + item.fallback_list()
    for code in codes:
        fact = fact_lookup.get(code.lower())
        if fact:
            return fact
    return None


def _calculate_analysis(primary_fact: Fact | None, comparison_fact: Fact | None):
    primary_value = _as_decimal(primary_fact.value) if primary_fact else None
    comparison_value = _as_decimal(comparison_fact.value) if comparison_fact else None

    delta_value = None
    delta_percent = None

    if primary_value is not None and comparison_value is not None:
        delta_value = primary_value - comparison_value
        if comparison_value != 0:
            delta_percent = (delta_value / comparison_value) * Decimal("100")

    return {
        "primary_value_display": _format_decimal(primary_value),
        "comparison_value_display": _format_decimal(comparison_value),
        "delta_value_display": _format_decimal(delta_value),
        "delta_percent_display": _format_percent(delta_percent),
    }


def _as_decimal(value: str | None):
    if value is None:
        return None
    cleaned = value.replace(",", "")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, AttributeError):
        return None


def _format_decimal(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}"


def _format_percent(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}%"


def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah keluar dari sesi admin.")
    return redirect("home")
