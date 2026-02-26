"""
conditional_views.py

This module contains view functions for handling conditional formatting operations.
"""

from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from urllib.parse import parse_qs

from base.methods import get_key_instances
from horilla.decorators import hx_request_required, login_required, permission_required
from payroll.forms.conditional_forms import ConditionalFormattingForm
from payroll.models.models import ConditionalFormatting


@login_required
@permission_required("payroll.view_conditionalformatting")
def conditional_formatting_view(request):
    """
    Display the conditional formatting view.
    """
    rules = ConditionalFormatting.objects.all()
    template = "payroll/conditional/conditional_formatting_view.html"
    context = {"rules": rules}
    return render(request, template, context)


@login_required
@hx_request_required
@permission_required("payroll.add_conditionalformatting")
def create_conditional_formatting(request):
    """
    Create a conditional formatting rule.
    """
    form = ConditionalFormattingForm()
    if request.method == "POST":
        form = ConditionalFormattingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Conditional formatting rule created successfully"))
            form = ConditionalFormattingForm()
            if len(ConditionalFormatting.objects.filter()) == 1:
                return HttpResponse("<script>window.location.reload()</script>")
    return render(
        request,
        "payroll/conditional/conditional_formatting_creation.html",
        {
            "form": form,
        },
    )


@login_required
@hx_request_required
@permission_required("payroll.change_conditionalformatting")
def update_conditional_formatting(request, rule_id):
    """
    Update an existing conditional formatting rule.
    """
    rule = ConditionalFormatting.find(rule_id)
    if not rule:
        messages.error(request, _("Conditional formatting rule not found"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    
    form = ConditionalFormattingForm(instance=rule)
    if request.method == "POST":
        form = ConditionalFormattingForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, _("Conditional formatting rule updated successfully"))
    
    return render(
        request,
        "payroll/conditional/conditional_formatting_edit.html",
        {
            "form": form,
        },
    )


@login_required
@hx_request_required
@permission_required("payroll.delete_conditionalformatting")
def delete_conditional_formatting(request, rule_id):
    """
    Delete a conditional formatting rule.
    """
    try:
        rule = ConditionalFormatting.find(rule_id)
        if rule:
            try:
                rule.delete()
                messages.info(request, _("Conditional formatting rule successfully deleted"))
            except ProtectedError:
                messages.error(
                    request,
                    _("Conditional formatting rule is in use. Remove dependencies first."),
                )
        else:
            messages.error(request, _("This conditional formatting rule was not found"))
    except Exception as e:
        messages.error(
            request, _("An error occurred while trying to delete the rule")
        )
    
    if not ConditionalFormatting.objects.exists():
        return HttpResponse("<script>window.location.reload()</script>")
    return redirect(conditional_formatting_search)


@login_required
@hx_request_required
@permission_required("payroll.view_conditionalformatting")
def conditional_formatting_search(request):
    """
    Display the conditional formatting search view.
    """
    search = request.GET.get("search") if request.GET.get("search") else ""
    module_type = request.GET.get("module_type", "")
    
    rules = ConditionalFormatting.objects.filter(name__icontains=search)
    if module_type:
        rules = rules.filter(module_type=module_type)
    
    previous_data = request.GET.urlencode()
    data_dict = parse_qs(previous_data)
    get_key_instances(ConditionalFormatting, data_dict)
    
    context = {
        "rules": rules,
        "pd": previous_data,
        "filter_dict": data_dict,
    }
    return render(request, "payroll/conditional/conditional_formatting_list.html", context)


@login_required
@permission_required("payroll.change_conditionalformatting")
def update_conditional_code(request, pk):
    """
    Ajax method to update python code of conditional formatting rule
    """
    code = request.POST["code"]
    rule = ConditionalFormatting.objects.get(pk=pk)
    if not rule.python_code == code:
        rule.python_code = code
        rule.save()
        messages.success(request, _("Python code saved successfully!"))
    return JsonResponse({"message": "success"})
