/**
 * Toggle conditional formatting dropdown visibility
 * Shows/hides the conditional_formatting_rule dropdown based on use_conditional_formatting toggle
 */
function toggleConditionalFormattingDropdown(checkbox) {
    const isChecked = checkbox.is(':checked');
    const dropdownContainer = $('#id_conditional_formatting_rule').closest('p, .oh-input-group, div');
    
    if (isChecked) {
        dropdownContainer.show();
    } else {
        dropdownContainer.hide();
        // Clear selection when hiding
        $('#id_conditional_formatting_rule').val('');
    }
}

// Initialize on page load
$(document).ready(function() {
    // Check initial state and hide/show dropdown accordingly
    const checkbox = $('#id_use_conditional_formatting');
    if (checkbox.length) {
        // Set initial state
        toggleConditionalFormattingDropdown(checkbox);
        
        // Also trigger on change
        checkbox.on('change', function() {
            toggleConditionalFormattingDropdown($(this));
        });
    }
});
