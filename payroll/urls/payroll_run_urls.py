"""
URL patterns for payroll run operations.
"""

from django.urls import path

from payroll.views import payroll_run_views

urlpatterns = [
    path(
        "payroll-runs/",
        payroll_run_views.payroll_run_list,
        name="payroll-run-list",
    ),
    path(
        "payroll-runs/create/",
        payroll_run_views.create_payroll_run,
        name="create-payroll-run",
    ),
    path(
        "payroll-runs/<int:run_id>/update/",
        payroll_run_views.update_payroll_run,
        name="update-payroll-run",
    ),
    path(
        "payroll-runs/<int:run_id>/view/",
        payroll_run_views.view_payroll_run,
        name="view-payroll-run",
    ),
    path(
        "payroll-runs/<int:run_id>/delete/",
        payroll_run_views.delete_payroll_run,
        name="delete-payroll-run",
    ),
    path(
        "payroll-runs/<int:run_id>/update-status/",
        payroll_run_views.update_payroll_run_status,
        name="update-payroll-run-status",
    ),
]
