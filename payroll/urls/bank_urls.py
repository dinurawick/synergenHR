"""
bank_urls.py

URL patterns for bank management
"""

from django.urls import path

from employee import views as employee_views

urlpatterns = [
    # Bank Management URLs
    path("banks/", employee_views.view_banks, name="view-banks"),
    path("bank/create/", employee_views.create_bank, name="create-bank"),
    path("bank/update/<int:obj_id>/", employee_views.update_bank, name="update-bank"),
    path("bank/delete/<int:obj_id>/", employee_views.delete_bank, name="delete-bank"),
    path("branches/", employee_views.view_branches, name="view-branches"),
    path("branch/create/", employee_views.create_branch, name="create-branch"),
    path("branch/update/<int:obj_id>/", employee_views.update_branch, name="update-branch"),
    path("branch/delete/<int:obj_id>/", employee_views.delete_branch, name="delete-branch"),
    # API endpoints for cascading dropdowns
    path("api/banks/", employee_views.get_banks_api, name="get-banks-api"),
    path("api/branches/", employee_views.get_branches_api, name="get-branches-api"),
]
