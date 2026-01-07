from django.contrib import admin

from .models import Company, Context, Fact, Filing, ReportTemplate, TemplateItem


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "created_at")
    search_fields = ("ticker", "name")


@admin.register(Filing)
class FilingAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "period_label",
        "period_end",
        "instant_date",
        "uploaded_at",
    )
    list_filter = ("company",)
    search_fields = ("company__ticker", "period_label")


@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ("filing", "context_id", "period_type", "start_date", "end_date")
    list_filter = ("period_type",)
    search_fields = ("context_id",)


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    list_display = ("filing", "name", "value", "context")
    search_fields = ("name", "value")
    list_filter = ("filing",)


class TemplateItemInline(admin.TabularInline):
    model = TemplateItem
    extra = 1


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TemplateItemInline]


@admin.register(TemplateItem)
class TemplateItemAdmin(admin.ModelAdmin):
    list_display = ("template", "label", "primary_fact", "order", "level")
    list_filter = ("template",)
