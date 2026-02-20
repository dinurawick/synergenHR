function conditionalVisibility() {
  if (!$("#id_is_condition_based").is(":checked")) {
    $('[onclick="conditionAdd()"]').parent().hide()
    $("#conditionContainer").hide();
    $("#id_field, #id_value, #id_condition").hide();
    $("#id_field, #id_value, #id_condition").parent().hide();
    $("[for='id_field'], [for='id_value'], [for='id_condition']").hide();
    $("[for='id_field'], [for='id_value'], [for='id_condition']")
      .parent()
      .hide();
  } else {
    $("#conditionContainer").show();
    $('[onclick="conditionAdd()"]').parent().show()
    $("#id_field, #id_value, #id_condition").show();
    $("#id_field, #id_value, #id_condition").parent().show();
    $("[for='id_field'], [for='id_value'], [for='id_condition']").show();
    $("[for='id_field'], [for='id_value'], [for='id_condition']")
      .parent()
      .show();
  }

  if ($("#id_is_tax").is(":checked")) {
    $("#id_is_fixed").prop("checked", false);
    $("#id_based_on,[for=id_based_on], #id_rate, [for=id_rate]").show();
    $("#id_based_on,[for=id_based_on], #id_rate, [for=id_rate]")
      .parent()
      .show();
    $(
      "#id_is_condition_based,[for=id_is_condition_based],#id_field,[for=field],#id_condition,[for=condition],#id_value,[for=id_value]"
    ).hide();
    $(
      "#id_is_condition_based,[for=id_is_condition_based],#id_field,[for=field],#id_condition,[for=condition],#id_value,[for=id_value]"
    )
      .parent()
      .hide();

    $(
      "#id_is_fixed,[for='id_is_fixed'],#id_amount,[for='id_amount'],#id_employee_rate,[for=id_employee_rate],#id_is_pretax,[for=id_is_pretax] "
    ).hide();
    $(
      "#id_is_fixed,[for='id_is_fixed'],#id_amount,[for='id_amount'],#id_employee_rate,[for=id_employee_rate],#id_is_pretax,[for=id_is_pretax] "
    )
      .parent()
      .hide();
  } else {
    $("#id_based_on,[for=id_based_on], #id_rate, [for=id_rate]").hide();
    $("#id_based_on,[for=id_based_on], #id_rate, [for=id_rate]")
      .parent()
      .hide();
    $(
      "#id_is_fixed,[for='id_is_fixed'],#id_amount,[for='id_amount'],#id_employee_rate,[for=id_employee_rate],#id_is_pretax,[for=id_is_pretax] "
    ).show();
    $(
      "#id_is_fixed,[for='id_is_fixed'],#id_amount,[for='id_amount'],#id_employee_rate,[for=id_employee_rate],#id_is_pretax,[for=id_is_pretax] "
    )
      .parent()
      .show();
    
    // Force show is_pretax field explicitly
    $("#id_is_pretax").show().parent().show();
    $("[for=id_is_pretax]").show().parent().show();
  }

  if (!$("#id_is_fixed").is(":checked")) {
    $("#id_based_on, #id_rate").show();
    $("#id_based_on, #id_rate").parent().show();
    $("[for='id_based_on'], [for='id_rate']").show();
    $("[for='id_based_on'], [for='id_rate']").parent().show();
    $("#id_amount").hide();
    $("#id_amount").parent().hide();
    $("[for='id_amount']").hide();
    $("[for='id_amount']").parent().hide();
    $("#id_employer_rate, [for=id_employer_rate]").show();
    $("#id_employer_rate, [for=id_employer_rate]").parent().show();
  } else {
    $("#id_based_on, #id_rate").hide();
    $("#id_based_on, #id_rate").parent().hide();
    $("[for='id_based_on'], [for='id_rate']").hide();
    $("[for='id_based_on'], [for='id_rate']").parent().hide();
    $("#id_amount").show();
    $("#id_amount").parent().show();
    $("[for='id_amount']").show();
    $("[for='id_amount']").parent().show();
    $("#id_employer_rate, [for=id_employer_rate]").hide();
    $("#id_employer_rate, [for=id_employer_rate]").parent().hide();
  }
  if ($("#id_is_fixed").is(":checked") && !$("#id_is_tax").is(":checked")) {
    $("#id_based_on, [for=id_based_on],#id_rate,[for=id_rate]").hide();
    $("#id_based_on, [for=id_based_on],#id_rate,[for=id_rate]").parent().hide();
    $("#id_amount,[for=id_amount]").show();
    $("#id_amount,[for=id_amount]").parent().show();
  }

  if ($("#id_include_active_employees").is(":checked")) {
    $("#id_is_condition_based").prop("checked",false)
    
    // Only fetch if not already populated
    if (!$("#id_specific_employees").data('employees-loaded')) {
      // Fetch and populate active employees
      $.ajax({
        url: '/payroll/get-active-employees',
        method: 'GET',
        success: function(data) {
          // Clear the select completely and rebuild
          $("#id_specific_employees").empty();
          
          // Add all active employees as options and select them
          data.employees.forEach(function(employee) {
            var newOption = new Option(employee.text, employee.id, true, true);
            $("#id_specific_employees").append(newOption);
          });
          
          // Mark as loaded
          $("#id_specific_employees").data('employees-loaded', true);
          
          // Trigger change to update Select2
          $("#id_specific_employees").trigger('change');
        }
      });
    }
    
    // Show the specific employees field so users can remove individuals
    $("#id_specific_employees, [for=id_specific_employees]").show();
    $("#id_specific_employees, [for=id_specific_employees]").parent().show();
    
    // Hide the Filter button/popup for specific_employees when include all is checked
    $("#id_specific_employees").closest('div').find('[data-toggle="oh-modal-toggle"]').hide();
    
    // Hide the Exclude Employees field when include all is checked
    $("#id_exclude_employees, [for=id_exclude_employees]").hide();
    $("#id_exclude_employees, [for=id_exclude_employees]").parent().hide();
    
    // Hide condition based fields
    $("#id_is_condition_based, [for=id_is_condition_based]").hide();
    $("#id_is_condition_based, [for=id_is_condition_based]").parent().hide();
    $(
      "#id_field,[for=id_field], #id_condition,[for=id_condition], #id_value,[for=id_value]"
    ).hide();
    $(
      "#id_field,[for=id_field], #id_condition,[for=id_condition], #id_value,[for=id_value]"
    )
      .parent()
      .hide();
  } else {
    // Clear the loaded flag when unchecked
    $("#id_specific_employees").data('employees-loaded', false);
    
    // Show the Filter button again when unchecked
    $("#id_specific_employees").closest('div').find('[data-toggle="oh-modal-toggle"]').show();
    
    $(
      "#id_specific_employees, [for=id_specific_employees],#id_is_condition_based, [for=id_is_condition_based]"
    ).show();
    $(
      "#id_specific_employees, [for=id_specific_employees],#id_is_condition_based, [for=id_is_condition_based]"
    )
      .parent()
      .show();
    if ($("#id_is_condition_based").is(":checked")) {
      $(
        "#id_field,[for=id_field], #id_condition,[for=id_condition], #id_value,[for=id_value]"
      ).show();
      $(
        "#id_field,[for=id_field], #id_condition,[for=id_condition], #id_value,[for=id_value]"
      )
        .parent()
        .show();
    }
  }

  if (
    $("#id_is_condition_based").is(":checked") &&
    !$("#id_include_active_employees").is(":checked")
  ) {
    $("#id_exclude_employees, [for=id_exclude_employees]").show();
    $("#id_exclude_employees, [for=id_exclude_employees]").parent().show();
  } else {
    $("#id_exclude_employees, [for=id_exclude_employees]").hide();
    $("#id_exclude_employees, [for=id_exclude_employees]").parent().hide();
  }
  if ($("#id_is_condition_based").is(":checked")) {
    $("#id_specific_employees,[for=id_specific_employees]").hide();
    $("#id_specific_employees,[for=id_specific_employees]").parent().hide();
  }

  if (
    $("#id_has_max_limit").is(":checked") &&
    !$("#id_is_fixed").is(":checked")
  ) {
    $("#id_maximum_amount, [for=id_maximum_amount]").show();
    $("#id_maximum_amount, [for=id_maximum_amount]").parent().show();
  } else {
    $("#id_maximum_amount, [for=id_maximum_amount]").hide();
    $("#id_maximum_amount, [for=id_maximum_amount]").parent().hide();
  }

  if ($("#id_has_max_limit").is(":checked")) {
    $("#id_maximum_amount, [for=id_maximum_amount]").show();
    $("#id_maximum_amount, [for=id_maximum_amount]").parent().show();
    $("#id_maximum_unit,[for=id_maximum_unit]").show();
    $("#id_maximum_unit,[for=id_maximum_unit]").parent().show();
  } else {
    $("#id_maximum_amount, [for=id_maximum_amount]").hide();
    $("#id_maximum_amount, [for=id_maximum_amount]").parent().hide();
    $("#id_maximum_unit,[for=id_maximum_unit]").hide();
    $("#id_maximum_unit,[for=id_maximum_unit]").parent().hide();
  }

  if ($("#id_is_tax").is(":checked")) {
    $(
      "#id_is_condition_based,[for=id_is_condition_based],#id_field,[for=id_field],#id_condition,[for=id_condition],#id_value,[for=id_value]"
    ).hide();
    $(
      "#id_is_condition_based,[for=id_is_condition_based],#id_field,[for=id_field],#id_condition,[for=id_condition],#id_value,[for=id_value]"
    )
      .parent()
      .hide();
  }
  if ($("#id_update_compensation").val() != "") {
    $("#id_include_active_employees").prop("checked",false);
    $("#id_is_fixed").prop("checked",false);
    $(
      "#id_is_tax, [for=id_is_tax],#id_is_pretax, [for=id_is_pretax], #id_based_on,[for=id_based_on]"
    ).hide();
    $(
      "#id_is_tax, [for=id_is_tax],#id_is_pretax, [for=id_is_pretax], #id_based_on,[for=id_based_on]"
    )
      .parent()
      .hide();
    $(
      "#id_if_choice,[for=id_if_choice],#id_if_condition,[for=id_if_condition],#id_is_fixed,[for=id_is_fixed],#id_include_active_employees,[for=id_include_active_employees],#id_is_condition_based,[for=id_is_condition_based]"
    ).hide();
    $(
      "#id_if_choice,[for=id_if_choice],#id_if_condition,[for=id_if_condition],#id_is_fixed,[for=id_is_fixed],#id_include_active_employees,[for=id_include_active_employees],#id_is_condition_based,[for=id_is_condition_based]"
    )
      .parent()
      .hide();
    $(
      "#id_field,[for=id_field],#id_condition,[for=id_condition],#id_value,[for=id_value]"
    ).hide();
    $(
      "#id_field,[for=id_field],#id_condition,[for=id_condition],#id_value,[for=id_value]"
    )
      .parent()
      .hide();
    $(
      "#id_has_max_limit,[for=id_has_max_limit],#id_maximum_amount, [for=id_maximum_amount],#id_maximum_unit,[for=id_maximum_unit]"
    ).hide();
    $(
      "#id_has_max_limit,[for=id_has_max_limit],#id_maximum_amount, [for=id_maximum_amount],#id_maximum_unit,[for=id_maximum_unit]"
    )
      .parent()
      .hide();
    $("#id_amount,[for=id_amount]").show();
    $("#id_amount,[for=id_amount]").parent().show();
    $("#id_if_amount,[for=id_if_amount]").hide();
    $("#id_is_condition_based").prop("checked", false);
    $("#id_rate:hidden,[for=id_rate]:hidden,#id_employer_rate:hidden,[for=id_employer_rate]:hidden").show();
    $("#id_rate:hidden,[for=id_rate]:hidden,#id_employer_rate:hidden,[for=id_employer_rate]:hidden").parent().show();
  } else {
    $("#id_include_active_employees,[for=id_include_active_employees]").show();
    $("#id_include_active_employees,[for=id_include_active_employees]")
      .parent()
      .show();

    $("#id_has_max_limit,[for=id_has_max_limit]").show();
    $("#id_has_max_limit,[for=id_has_max_limit]").parent().show();
    if ($("#id_has_max_limit").is(":checked")) {
      $(
        "#id_maximum_amount, [for=id_maximum_amount],#id_maximum_unit,[for=id_maximum_unit]"
      ).show();
      $(
        "#id_maximum_amount, [for=id_maximum_amount],#id_maximum_unit,[for=id_maximum_unit]"
      ).parent().show();
    }
    $("#id_is_tax,[for=id_is_tax],#id_if_choice,[for=id_if_choice],#id_if_value,[for=id_if_value],#id_if_condition,[for=id_if_condition],#id_if_amount,[for=id_if_amount]").show();
    $("#id_is_tax,[for=id_is_tax],#id_if_choice,[for=id_if_choice],#id_if_value,[for=id_if_value],#id_if_condition,[for=id_if_condition],#id_if_amount,[for=id_if_amount]").parent().show();
  }
  if ($("#id_is_fixed").is(":checked")) {
    $("#id_has_max_limit").parent().parent().hide();
    $("#id_maximum_unit,#id_maximum_amount").parent().hide();
  }
  else {
    $("#id_has_max_limit").parent().parent().show();
    if ($("#id_has_max_limit").is(":checked")) {

      $("#id_maximum_unit,#id_maximum_amount").parent().show();
    }

  }
}
$(document).ready(function () {
  $("input[type='checkbox'], select, input[type='radio']").change(function (e) {
    e.preventDefault();
    conditionalVisibility();
  });
  $("#id_is_condition_based").parent().parent().attr("class","col-12")
  $("#id_condition, #id_field, #id_value").parent().attr("class", "col-12 col-md-4 condition-highlight");
  addMore = $(`
  <div class="mt-3" style="
  display: inline-block;
  margin-top: 0 !important;
  position: relative;
  top: -17px;
  left: 36px;">
  <div class="m-1 p-1"onclick="conditionAdd()" align="center" style="border-radius:15px; width:25px;border:solid 1px green;cursor:pointer;display:inline;" title="Add More">
  +
    </div>

    </div>
    `)

  // Adding add more mutton on the condition based check box
  $('[name="is_condition_based"]').parent().after(addMore);

  // Listen for changes on specific_employees to sync the dropdown options
  $('#id_specific_employees').on('change', function() {
    if ($("#id_include_active_employees").is(":checked")) {
      // Get currently selected values
      var selectedValues = $(this).val() || [];
      
      // Update the options to only show selected employees
      // This removes unselected ones from the dropdown
      var currentOptions = [];
      $(this).find('option').each(function() {
        if (selectedValues.includes($(this).val())) {
          currentOptions.push({
            id: $(this).val(),
            text: $(this).text()
          });
        }
      });
      
      // Rebuild the select with only selected options
      $(this).empty();
      currentOptions.forEach(function(opt) {
        var option = new Option(opt.text, opt.id, true, true);
        $('#id_specific_employees').append(option);
      });
      
      // Trigger change to update Select2 display
      $(this).trigger('change.select2');
      
      // Remove title attributes from the selected items to prevent tooltips
      setTimeout(function() {
        $('#selectContainerid_specific_employees .select2-selection__choice').removeAttr('title');
      }, 100);
    }
  });
  
  // Also remove tooltips on initial load when include all is checked
  setTimeout(function() {
    if ($("#id_include_active_employees").is(":checked")) {
      $('#selectContainerid_specific_employees .select2-selection__choice').removeAttr('title');
    }
  }, 500);

  // Add custom CSS for specific_employees select2
  $('<style>')
    .prop('type', 'text/css')
    .html(`
      /* Increase height of the selected items box to show more names */
      #selectContainerid_specific_employees .select2-container .select2-selection {
        max-height: 300px !important;
        overflow-y: auto !important;
        padding: 5px !important;
      }
      
      /* Position the dropdown to the RIGHT side of the field */
      .select2-container--open .select2-dropdown--below {
        position: absolute !important;
        left: 100% !important;
        top: 0 !important;
        margin-left: 10px !important;
      }
      
      /* Make dropdown scrollable with reasonable height */
      .select2-results {
        max-height: 300px !important;
        overflow-y: auto !important;
      }
      
      /* Position the selection choice tooltips to the right */
      #selectContainerid_specific_employees .select2-selection__choice {
        position: relative !important;
      }
      
      #selectContainerid_specific_employees .select2-selection__choice__display {
        position: relative !important;
      }
      
      /* Move any tooltips/titles to the right side */
      #selectContainerid_specific_employees .select2-selection__choice[title]:hover::after {
        content: attr(title) !important;
        position: absolute !important;
        left: 100% !important;
        top: 0 !important;
        margin-left: 10px !important;
        background: #333 !important;
        color: white !important;
        padding: 5px 10px !important;
        border-radius: 4px !important;
        white-space: nowrap !important;
        z-index: 9999 !important;
      }
    `)
    .appendTo('head');

});



conditionContainer = $(`
<div id="conditionContainer" class="col-12 col-md-12">
</div>
`)
// Add condition container
$('#id_value').parent().after(conditionContainer)

function conditionAdd() {
  let conditionSet = $(
    `
    <div class="row">
      <div class="col-12 col-md-4 condition-highlight">
        ${$("[for=id_field]").clone().attr("class", "style-widget form-control oh-label__info").prop("outerHTML")}
        ${$("#id_field").clone().attr("name", "other_fields").attr("class", "style-widget form-control").prop("outerHTML")}
      </div>
      <div class="col-12 col-md-4 condition-highlight">
        ${$("[for=id_condition]").clone().attr("class", "style-widget form-control oh-label__info").prop("outerHTML")}
        ${$("#id_condition").clone().attr("name", "other_conditions").attr("class", "style-widget form-control").prop("outerHTML")}
      </div>
      <div class="col-12 col-md-4 condition-highlight">
        <div class="d-flex">
          ${$("[for=id_value]").clone().attr("class", "style-widget form-control oh-label__info").prop("outerHTML")}
          <div class="m-1 p-1" onclick="$(this).closest('.row').remove()" align="center" style="border-radius:15px; width:25px;border:solid 1px red;cursor:pointer;display:inline;">
            -
          </div>
        </div>
        ${$("#id_value").clone().attr("name", "other_values").attr("class", "style-widget form-control").prop("outerHTML")}
      </div>
    </div>
    `
  );

  $("#conditionContainer").append(conditionSet);
}
conditionalVisibility();

// Force show is_pretax field on page load and form changes
$(document).ready(function() {
  // Ensure is_pretax field is always visible when not in tax mode
  function forceShowIsPretax() {
    if (!$("#id_is_tax").is(":checked")) {
      $("#id_is_pretax, [for=id_is_pretax]").show().parent().show();
    }
  }
  
  // Call on page load
  forceShowIsPretax();
  
  // Call on any form change
  $("input, select").on("change", function() {
    setTimeout(forceShowIsPretax, 100);
  });
});
