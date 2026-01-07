from django import forms

from .models import ReportTemplate, TemplateItem


class XBRLUploadForm(forms.Form):
    file = forms.FileField(label="File XBRL")
    overwrite = forms.BooleanField(
        required=False,
        initial=False,
        label="Timpa data jika periode sudah ada",
        help_text="Centang jika ingin menimpa laporan periode yang sama.",
    )


class TemplateForm(forms.ModelForm):
    class Meta:
        model = ReportTemplate
        fields = ["name", "slug", "description"]


class TemplateItemForm(forms.ModelForm):
    class Meta:
        model = TemplateItem
        fields = ["template", "label", "primary_fact", "fallback_facts", "order", "level"]
        widgets = {
            "fallback_facts": forms.Textarea(attrs={"rows": 3}),
        }
