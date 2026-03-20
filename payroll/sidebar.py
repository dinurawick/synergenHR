"""
payroll/sidebar.py

"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Payroll")
IMG_SRC = "images/ui/wallet-outline.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse("view-payroll-dashboard"),
        "accessibility": "payroll.sidebar.dasbhoard_accessibility",
    },
    {
        "menu": trans("Contract"),
        "redirect": reverse("view-contract"),
        "accessibility": "payroll.sidebar.dasbhoard_accessibility",
    },
    {
        "menu": trans("Payroll Runs"),
        "redirect": reverse("payroll-run-list"),
        "accessibility": "payroll.sidebar.payroll_run_accessibility",
    },
    {
        "menu": trans("Pay Items"),
        "redirect": "#",
        "accessibility": "payroll.sidebar.pay_items_accessibility",
        "submenus": [
            {
                "menu": trans("Earnings"),
                "redirect": reverse("view-allowance"),
                "accessibility": "payroll.sidebar.allowance_accessibility",
            },
            {
                "menu": trans("Deductions"),
                "redirect": reverse("view-deduction"),
                "accessibility": "payroll.sidebar.deduction_accessibility",
            },
        ],
    },
    {
        "menu": trans("Payslips"),
        "redirect": reverse("view-payslip"),
    },
    {
        "menu": trans("Loan / Advanced Salary"),
        "redirect": reverse("view-loan"),
        "accessibility": "payroll.sidebar.loan_accessibility",
    },
    {
        "menu": trans("Encashments & Reimbursements"),
        "redirect": reverse("view-reimbursement"),
    },
    {
        "menu": trans("Tax"),
        "redirect": reverse("filing-status-view"),
        "accessibility": "payroll.sidebar.federal_tax_accessibility",
    },
]


def dasbhoard_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_contract")


def allowance_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_allowance")


def deduction_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_deduction")


def loan_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_loanaccount")


def federal_tax_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_filingstatus")


def bank_management_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("employee.view_bank") or request.user.has_perm("employee.view_bankbranch")


def bank_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("employee.view_bank")


def branch_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("employee.view_bankbranch")


def payroll_run_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_payrollrun")
