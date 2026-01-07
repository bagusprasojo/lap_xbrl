"""
URL configuration for lapxbrl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from reports.views import (
    DeleteFilingView,
    FilingDetailView,
    HomeView,
    CompanyListView,
    PublicReportView,
    TemplateDetailView,
    TemplateListView,
    UploadXBRLView,
    logout_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", logout_view, name="logout"),
    path("dashboard/upload/", UploadXBRLView.as_view(), name="upload_xbrl"),
    path("dashboard/templates/", TemplateListView.as_view(), name="manage_templates"),
    path(
        "dashboard/templates/<int:template_id>/",
        TemplateDetailView.as_view(),
        name="manage_template_detail",
    ),
    path("dashboard/filings/<int:pk>/", FilingDetailView.as_view(), name="filing_detail"),
    path(
        "dashboard/filings/<int:pk>/delete/",
        DeleteFilingView.as_view(),
        name="delete_filing",
    ),
    path("", HomeView.as_view(), name="home"),
    path(
        "laporan/neraca/",
        PublicReportView.as_view(report_slug="neraca"),
        name="report_neraca",
    ),
    path(
        "laporan/laba-rugi/",
        PublicReportView.as_view(report_slug="laba-rugi"),
        name="report_laba_rugi",
    ),
    path(
        "laporan/arus-kas/",
        PublicReportView.as_view(report_slug="arus-kas"),
        name="report_arus_kas",
    ),
    path("emiten/", CompanyListView.as_view(), name="company_list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
