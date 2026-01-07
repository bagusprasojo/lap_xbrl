from django.db import models


class Company(models.Model):
    ticker = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255, blank=True)
    entity_code = models.CharField(max_length=32, blank=True)
    entity_name = models.CharField(max_length=255, blank=True)
    entity_main_industry = models.CharField(max_length=255, blank=True)
    sector = models.CharField(max_length=255, blank=True)
    subsector = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    subindustry = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ticker"]

    def __str__(self) -> str:
        return self.ticker


class Filing(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="filings"
    )
    period_label = models.CharField(max_length=128, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    instant_date = models.DateField(null=True, blank=True)
    context_reference = models.CharField(max_length=255, blank=True)
    document_type = models.CharField(max_length=128, blank=True)
    source_filename = models.CharField(max_length=255, blank=True)
    xbrl_file = models.FileField(upload_to="xbrl/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_end", "-instant_date", "-uploaded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "period_label"], name="unique_company_period_label"
            )
        ]

    def __str__(self) -> str:
        if self.period_label:
            return f"{self.company.ticker} - {self.period_label}"
        return f"Filing {self.pk}"


class Context(models.Model):
    filing = models.ForeignKey(
        Filing, on_delete=models.CASCADE, related_name="contexts"
    )
    context_id = models.CharField(max_length=128)
    entity_identifier = models.CharField(max_length=128, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    instant_date = models.DateField(null=True, blank=True)
    period_type = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["context_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["filing", "context_id"], name="unique_context_per_filing"
            )
        ]

    def __str__(self) -> str:
        return f"{self.context_id}"


class Fact(models.Model):
    filing = models.ForeignKey(Filing, on_delete=models.CASCADE, related_name="facts")
    context = models.ForeignKey(
        Context, null=True, blank=True, on_delete=models.SET_NULL, related_name="facts"
    )
    name = models.CharField(max_length=255)
    namespace = models.CharField(max_length=255, blank=True)
    value = models.TextField(blank=True)
    decimals = models.CharField(max_length=32, blank=True)
    unit = models.CharField(max_length=64, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name", "order", "id"]

    def __str__(self) -> str:
        return self.name


class ReportTemplate(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TemplateItem(models.Model):
    template = models.ForeignKey(
        ReportTemplate, on_delete=models.CASCADE, related_name="items"
    )
    label = models.CharField(max_length=255)
    primary_fact = models.CharField(max_length=255)
    fallback_facts = models.TextField(
        blank=True,
        help_text="Masukkan 1 kode item per baris sebagai fallback bila primary kosong.",
    )
    order = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.template.name} - {self.label}"

    def fallback_list(self) -> list[str]:
        text = self.fallback_facts or ""
        return [line.strip() for line in text.splitlines() if line.strip()]
