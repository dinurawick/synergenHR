"""
payroll/sidebar.py

"""

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as trans

MENU = trans("Payroll")
IMG_SRC = "images/ui/wallet-outline.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse_lazy("view-payroll-dashboard"),
        "accessibility": "payroll.sidebar.dasbhoard_accessibility",
    },
    {
        "menu": trans("Contract"),
        "redirect": reverse_lazy("view-contract"),
        "accessibility": "payroll.sidebar.dasbhoard_accessibility",
    },
    {
        "menu": trans("Payroll Runs"),
        "redirect": reverse_lazy("payroll-run-list"),
        "accessibility": "payroll.sidebar.payroll_run_accessibility",
    },
    {
        "menu": trans("Pay Items"),
        "redirect": "#",
        "accessibility": "payroll.sidebar.pay_items_accessibility",
        "submenus": [
            {
                "menu": trans("Earnings"),
                "redirect": reverse_lazy("view-allowance"),
                "accessibility": "payroll.sidebar.allowance_accessibility",
            },
            {
                "menu": trans("Deductions"),
                "redirect": reverse_lazy("view-deduction"),
                "accessibility": "payroll.sidebar.deduction_accessibility",
            },
        ],
    },
    {
        "menu": trans("Payslips"),
        "redirect": reverse_lazy("view-payslip"),
    },
    {
        "menu": trans("Loan / Advanced Salary"),
        "redirect": reverse_lazy("view-loan"),
        "accessibility": "payroll.sidebar.loan_accessibility",
    },
    {
        "menu": trans("Encashments & Reimbursements"),
        "redirect": reverse_lazy("view-reimbursement"),
    },
    {
        "menu": trans("Tax"),
        "redirect": reverse_lazy("filing-status-view"),
        "accessibility": "payroll.sidebar.federal_tax_accessibility",
    },
    {
        "menu": trans("Bank Management"),
        "redirect": "#",
        "accessibility": "payroll.sidebar.bank_management_accessibility",
        "submenus": [
            {
                "menu": trans("Banks"),
                "redirect": "/payroll/banks/",
                "accessibility": "payroll.sidebar.bank_accessibility",
            },
            {
                "menu": trans("Branches"),
                "redirect": "/payroll/branches/",
                "accessibility": "payroll.sidebar.branch_accessibility",
            },
        ],
    },
]


def dasbhoard_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_contract")


def pay_items_accessibility(request, submenu, user_perms, *args, **kwargs):
    return request.user.has_perm("payroll.view_allowance") or request.user.has_perm("payroll.view_deduction")


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
