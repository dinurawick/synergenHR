"""
conditional_urls.py

URL patterns for conditional formatting
"""

from django.urls import path
from payroll.views import conditional_views

urlpatterns = [
    path(
        "conditional-formatting-view/",
        conditional_views.conditional_formatting_view,
        name="conditional-formatting-view",
    ),
    path(
        "create-conditional-formatting/",
        conditional_views.create_conditional_formatting,
        name="create-conditional-formatting",
    ),
    path(
        "update-conditional-formatting/<int:rule_id>/",
        conditional_views.update_conditional_formatting,
        name="update-conditional-formatting",
    ),
    path(
        "delete-conditional-formatting/<int:rule_id>/",
        conditional_views.delete_conditional_formatting,
        name="delete-conditional-formatting",
    ),
    path(
        "conditional-formatting-search/",
        conditional_views.conditional_formatting_search,
        name="conditional-formatting-search",
    ),
    path(
        "update-conditional-code/<int:pk>/",
        conditional_views.update_conditional_code,
        name="update-conditional-code",
    ),
]
