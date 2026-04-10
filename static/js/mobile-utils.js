/**
 * Mobile-friendly utilities for better performance on mobile devices
 */

// Detect if user is on mobile device
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           window.innerWidth <= 768;
}

// Mobile-friendly page reload with loading indicator
function mobileReload(delay = 1000) {
    if (isMobileDevice()) {
        // Show loading indicator
        var loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'mobile-loading-overlay';
        loadingOverlay.innerHTML = `
            <div style="
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100%; 
                height: 100%; 
                background: rgba(0,0,0,0.7); 
                z-index: 9999; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                color: white;
                font-size: 16px;
            ">
                <div style="text-align: center;">
                    <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto 10px;"></div>
                    <div>Loading...</div>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(loadingOverlay);
        
        // Delay reload to show loading indicator
        setTimeout(function() {
            window.location.reload();
        }, delay);
    } else {
        // Desktop - immediate reload
        window.location.reload();
    }
}

// Batch DOM operations for better mobile performance
function batchDOMOperations(operations, batchSize = 50) {
    if (!Array.isArray(operations)) {
        return;
    }
    
    function processBatch(startIndex) {
        var endIndex = Math.min(startIndex + batchSize, operations.length);
        
        for (var i = startIndex; i < endIndex; i++) {
            if (typeof operations[i] === 'function') {
                operations[i]();
            }
        }
        
        if (endIndex < operations.length) {
            if (isMobileDevice()) {
                // Use requestAnimationFrame for smooth updates on mobile
                requestAnimationFrame(function() {
                    processBatch(endIndex);
                });
            } else {
                // Desktop - process immediately
                processBatch(endIndex);
            }
        }
    }
    
    processBatch(0);
}

// Debounce function to prevent rapid API calls on mobile
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Mobile-friendly AJAX with loading indicators
function mobileAjax(options) {
    var defaultOptions = {
        timeout: isMobileDevice() ? 30000 : 10000, // Longer timeout for mobile
        beforeSend: function() {
            if (isMobileDevice() && options.showLoading !== false) {
                // Show loading indicator
                if (!document.getElementById('ajax-loading')) {
                    var loading = document.createElement('div');
                    loading.id = 'ajax-loading';
                    loading.innerHTML = '<div style="position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; z-index: 1000;"><i class="fa fa-spinner fa-spin"></i> Loading...</div>';
                    document.body.appendChild(loading);
                }
            }
        },
        complete: function() {
            // Remove loading indicator
            var loading = document.getElementById('ajax-loading');
            if (loading) {
                loading.remove();
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX Error:', error);
            if (isMobileDevice()) {
                alert('Network error. Please check your connection and try again.');
            }
        }
    };
    
    // Merge options
    var finalOptions = Object.assign({}, defaultOptions, options);
    
    return $.ajax(finalOptions);
}

// Replace all location.reload() calls with mobile-friendly version
if (typeof window !== 'undefined') {
    // Override location.reload for mobile optimization
    var originalReload = window.location.reload;
    window.location.reload = function(forceReload) {
        if (isMobileDevice()) {
            mobileReload();
        } else {
            originalReload.call(window.location, forceReload);
        }
    };
}