/**
 * Ads Module JavaScript
 * Handles ad display, tracking, and management
 */

// Ad Display Functions
function displayAd(slotCode, containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    // Set loading state
    container.innerHTML = '<div class="ad-loading"><i class="fa fa-spinner fa-spin"></i> Loading ad...</div>';

    // Fetch ad from server
    fetch('/ads/api/ad/' + slotCode + '/')
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Ad not found');
            }
            return response.json();
        })
        .then(function(ad) {
            renderAd(ad, container);
        })
        .catch(function(error) {
            console.log('Error loading ad:', error);
            container.innerHTML = '<div class="ad-error">No ad available</div>';
        });
}

function renderAd(ad, container) {
    var html = '';

    switch(ad.ad_type) {
        case 'image':
            html = renderImageAd(ad);
            break;
        case 'html':
            html = ad.html_content;
            break;
        case 'script':
            html = '<script>' + ad.script_content + '</script>';
            break;
        case 'video':
            html = renderVideoAd(ad);
            break;
        default:
            html = '<div class="ad-error">Unknown ad type</div>';
    }

    container.innerHTML = html;
    
    // Track impression
    trackAdImpression(ad.id);
}

function renderImageAd(ad) {
    var url = ad.url || '#';
    var target = ad.target || '_blank';
    var title = ad.title || '';
    var description = ad.description || '';
    
    var html = '<div class="ad-container">';
    
    if (ad.url) {
        html += '<a href="' + url + '" target="' + target + '" onclick="trackAdClick(\'' + ad.id + '\')" style="text-decoration: none; display: inline-block;">';
    }
    
    if (ad.image) {
        html += '<img src="' + ad.image_url + '" alt="' + (ad.image_alt || ad.name) + '" title="' + title + '" style="max-width: 100%; height: auto; display: block;">';
    }
    
    if (title) {
        html += '<div style="text-align: center; margin-top: 8px; font-size: 14px; color: #333;">' + title + '</div>';
    }
    
    if (description) {
        html += '<div style="text-align: center; margin-top: 4px; font-size: 12px; color: #666;">' + description + '</div>';
    }
    
    if (ad.url) {
        html += '</a>';
    }
    
    html += '</div>';
    
    return html;
}

function renderVideoAd(ad) {
    var url = ad.url || '#';
    var target = ad.target || '_blank';
    var title = ad.title || '';
    var description = ad.description || '';
    
    var html = '<div class="ad-container" style="text-align: center;">';
    
    if (ad.url) {
        html += '<a href="' + url + '" target="' + target + '" onclick="trackAdClick(\'' + ad.id + '\')" style="text-decoration: none; display: inline-block;">';
    }
    
    if (ad.video_embed_code) {
        html += '<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%;">';
        html += ad.video_embed_code;
        html += '</div>';
    } else if (ad.video_url) {
        html += '<video controls style="max-width: 100%; height: auto;"';
        if (ad.image) {
            html += ' poster="' + ad.image_url + '"';
        }
        html += '><source src="' + ad.video_url + '" type="video/mp4">Your browser does not support the video tag.</video>';
    }
    
    if (title) {
        html += '<div style="margin-top: 12px; font-size: 16px; font-weight: bold; color: #333;">' + title + '</div>';
    }
    
    if (description) {
        html += '<div style="margin-top: 8px; font-size: 14px; color: #666;">' + description + '</div>';
    }
    
    if (ad.url) {
        html += '</a>';
    }
    
    html += '</div>';
    
    return html;
}

// Ad Tracking Functions
function trackAdImpression(adId) {
    // Only track once per page load
    if (localStorage.getItem('ad_impression_' + adId)) {
        return;
    }
    
    fetch('/ads/track/impression/' + adId + '/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    }).then(function() {
        localStorage.setItem('ad_impression_' + adId, '1');
    }).catch(function(error) {
        console.log('Ad impression tracking failed:', error);
    });
}

function trackAdClick(adId) {
    fetch('/ads/track/click/' + adId + '/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    }).catch(function(error) {
        console.log('Ad click tracking failed:', error);
    });
    
    // Don't prevent default - let the link work
}

// Ad Management Functions
function toggleAdActive(adId, element) {
    var url = '/ads/' + adId + '/toggle-active/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        if (data.success) {
            var isActive = data.is_active;
            var btn = $(element);
            btn.removeClass('btn-danger btn-success');
            btn.addClass('btn-' + (isActive ? 'success' : 'danger'));
            btn.find('i').removeClass('fa-eye-slash fa-eye');
            btn.find('i').addClass(isActive ? 'fa-eye-slash' : 'fa-eye');
            
            // Update status in table
            btn.closest('tr').find('.status').removeClass('status-success status-warning');
            btn.closest('tr').find('.status').addClass('status-' + (isActive ? 'success' : 'warning'));
            btn.closest('tr').find('.status').text(isActive ? 'فعال' : 'غیرفعال');
        }
    }).catch(function(error) {
        console.log('Error toggling ad status:', error);
    });
}

function deleteAd(adId) {
    if (!confirm('Are you sure you want to delete this ad?')) {
        return false;
    }
    
    var form = document.getElementById('delete-form-' + adId);
    if (form) {
        form.submit();
    }
    
    return false;
}

// Ad Form Functions
function updateAdFormFields(adType) {
    // Hide all type-specific fields
    $('.image-field, .html-field, .script-field, .video-field').addClass('d-none');
    
    // Show fields for selected type
    if (adType === 'image') {
        $('.image-field').removeClass('d-none');
    } else if (adType === 'html') {
        $('.html-field').removeClass('d-none');
    } else if (adType === 'script') {
        $('.script-field').removeClass('d-none');
    } else if (adType === 'video') {
        $('.video-field').removeClass('d-none');
    }
}

// Ad Statistics Functions
function loadAdStats(adId) {
    fetch('/ads/api/stats/' + adId + '/')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            updateStatsDisplay(data);
        })
        .catch(function(error) {
            console.log('Error loading ad stats:', error);
        });
}

function updateStatsDisplay(data) {
    // Update stats display on the page
    if (data.impressions) {
        $('#stat-impressions').text(data.impressions);
    }
    if (data.clicks) {
        $('#stat-clicks').text(data.clicks);
    }
    if (data.ctr) {
        $('#stat-ctr').text(data.ctr.toFixed(2) + '%');
    }
}

// Ad Chart Functions
function createAdChart(canvasId, data, label) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: label,
                data: data.values,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    return chart;
}

// Utility Functions
function getCSRFToken() {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize on page load
jQuery(function($) {
    // Initialize ad type field visibility
    var adTypeSelect = $('#id_ad_type');
    if (adTypeSelect.length) {
        updateAdFormFields(adTypeSelect.val());
        adTypeSelect.change(function() {
            updateAdFormFields($(this).val());
        });
    }
    
    // Initialize toggle active buttons
    $('.toggle-active').click(function(e) {
        e.preventDefault();
        var adId = $(this).data('id');
        toggleAdActive(adId, this);
    });
    
    // Initialize delete forms
    $('.delete-form').submit(function(e) {
        return confirm('Are you sure you want to delete this item?');
    });
});

// Export functions for use in templates
window.AdDisplay = {
    displayAd: displayAd,
    renderAd: renderAd,
    trackAdImpression: trackAdImpression,
    trackAdClick: trackAdClick
};

window.AdManagement = {
    toggleAdActive: toggleAdActive,
    deleteAd: deleteAd,
    updateAdFormFields: updateAdFormFields
};

window.AdStats = {
    loadAdStats: loadAdStats,
    createAdChart: createAdChart
};
