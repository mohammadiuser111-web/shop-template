# Ads Module

## Overview
The Ads module provides comprehensive advertisement management for the shop-template project. It includes:
- Ad slot management
- Advertisement creation and management
- Impression and click tracking
- Statistics and reporting
- RESTful API

## Features

### Ad Slots
- Create and manage ad slots (positions) on your website
- Define dimensions (width, height) or make them responsive
- Use slot codes to display ads in templates

### Advertisements
- Support for multiple ad types: Image, HTML, JavaScript, Video
- Priority-based ad rotation
- Date-based scheduling (start/end dates)
- Target URLs and link behavior control

### Tracking
- Track impressions (views)
- Track clicks
- Calculate CTR (Click-Through Rate)
- User, IP, and session tracking

### Statistics and Reports
- View statistics for individual ads
- View statistics for ad slots
- Generate impression reports
- Generate click reports
- Generate performance reports
- View overall ad system statistics

## Installation

The Ads module is already included in the shop-template project. No additional installation is required.

## Configuration

### Settings
The module uses the following Django settings (already configured in the project):

```python
INSTALLED_APPS = [
    ...
    'apps.ads',
    ...
]
```

### Database
Run migrations to create the required tables:

```bash
python manage.py migrate ads
```

### Static Files
Collect static files:

```bash
python manage.py collectstatic
```

## Usage

### Creating Ad Slots

1. Go to the admin panel
2. Navigate to "Advertisements" > "Ad Slots"
3. Click "Add Ad Slot"
4. Enter slot details:
   - Name: Display name for the slot
   - Code: Unique identifier (used in templates)
   - Width/Height: Dimensions in pixels (optional for responsive slots)
   - Responsive: Enable for responsive slots
   - Active: Enable/disable the slot

### Creating Advertisements

1. Go to the admin panel
2. Navigate to "Advertisements" > "Advertisements"
3. Click "Add Advertisement"
4. Enter ad details:
   - Name: Internal name
   - Slot: Select an ad slot
   - Ad Type: Choose type (image, html, script, video)
   - Content: Based on ad type
   - Priority: Higher priority ads show more frequently
   - URL: Target URL for clicks
   - Start/End Date: Scheduling
   - Active: Enable/disable the ad

### Displaying Ads in Templates

Use the slot code to display ads in your templates:

```html
<!-- Simple display -->
{% include "ads/includes/ad_image.html" with ad=ad %}

<!-- Or use the display view -->
<img src="{% url 'ads:display_ad' 'header_banner' %}" alt="Ad">

<!-- For responsive ads -->
<div id="ad-container">
    <script>
        fetch('{% url "ads_api:ad_display" "header_banner" %}')
            .then(response => response.json())
            .then(ad => {
                // Render ad based on type
                document.getElementById('ad-container').innerHTML = ad.html_content;
            });
    </script>
</div>
```

### Tracking Impressions and Clicks

Impressions are automatically tracked when ads are displayed. Clicks are tracked when users click on ads.

For custom tracking:

```javascript
// Track impression
fetch('/ads/track/impression/' + adId + '/');

// Track click
fetch('/ads/track/click/' + adId + '/');
```

## API Usage

See [API Documentation](docs/API.md) for complete API reference.

### Example API Calls

```bash
# List ad slots
curl -X GET http://localhost:8000/api/v1/ads/slots/ -H "Authorization: Token YOUR_TOKEN"

# Create advertisement
curl -X POST http://localhost:8000/api/v1/ads/advertisements/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Ad", "slot_id": "uuid", "ad_type": "image", "is_active": true}'

# Get ad for display
curl -X GET http://localhost:8000/api/v1/ads/display/header_banner/

# Track impression
curl -X POST http://localhost:8000/api/v1/ads/track/impression/ad-uuid/

# Get statistics
curl -X GET http://localhost:8000/api/v1/ads/stats/ad-uuid/ -H "Authorization: Token YOUR_TOKEN"
```

## Models

### AdSlot
- `id`: UUID
- `name`: String (255)
- `code`: String (100, unique)
- `description`: Text (optional)
- `width`: Integer (optional)
- `height`: Integer (optional)
- `is_responsive`: Boolean
- `is_active`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

### Advertisement
- `id`: UUID
- `name`: String (255)
- `slot`: ForeignKey to AdSlot
- `ad_type`: Choice (image, html, script, video)
- `image`: ImageField (optional)
- `image_alt`: String (optional)
- `html_content`: Text (optional)
- `script_content`: Text (optional)
- `video_url`: URL (optional)
- `video_embed_code`: Text (optional)
- `url`: URL (optional)
- `target`: Choice (_blank, _self, _parent, _top)
- `title`: String (optional)
- `description`: Text (optional)
- `priority`: Integer
- `start_date`: DateTime (optional)
- `end_date`: DateTime (optional)
- `is_active`: Boolean
- `created_by`: ForeignKey to User (optional)
- `created_at`: DateTime
- `updated_at`: DateTime
- `impression_count`: Integer
- `click_count`: Integer

### AdImpression
- `id`: UUID
- `ad`: ForeignKey to Advertisement
- `user`: ForeignKey to User (optional)
- `ip_address`: IPAddress (optional)
- `user_agent`: String (optional)
- `referrer`: URL (optional)
- `session_key`: String (optional)
- `created_at`: DateTime

### AdClick
- `id`: UUID
- `ad`: ForeignKey to Advertisement
- `impression`: ForeignKey to AdImpression (optional)
- `user`: ForeignKey to User (optional)
- `ip_address`: IPAddress (optional)
- `user_agent`: String (optional)
- `referrer`: URL (optional)
- `session_key`: String (optional)
- `created_at`: DateTime

## Services

### AdService
Main service for managing advertisements:
- `get_ad_slot(slot_code)`: Get ad slot by code
- `get_current_ad(slot_code, request)`: Get current ad for a slot
- `track_impression(ad, request)`: Track ad impression
- `track_click(ad, request)`: Track ad click
- `get_ad_stats(ad_id)`: Get ad statistics
- `get_slot_stats(slot_code)`: Get slot statistics
- `get_all_stats()`: Get overall statistics
- `clear_ad_cache(slot_code, ad_id)`: Clear ad cache

### AdRotationService
Service for rotating ads:
- `get_rotating_ads(slot_code, limit)`: Get ads for rotation
- `get_random_ad(slot_code)`: Get random ad for a slot

### AdReportService
Service for generating reports:
- `get_impression_report(date_from, date_to, slot)`: Get impression report
- `get_click_report(date_from, date_to, slot)`: Get click report
- `get_performance_report(date_from, date_to)`: Get performance report

## Testing

Run the ads tests:

```bash
python manage.py test apps.ads.tests
```

Or use the test runner script:

```bash
python apps/ads/tests/run_tests.py
```

## Customization

### Ad Types
To add a new ad type:
1. Add the type to `Advertisement.AD_TYPE_CHOICES`
2. Update the `get_ad_type_display()` method
3. Create a template for displaying the ad type
4. Update the form to handle the new type

### Tracking
To add custom tracking fields:
1. Add fields to the `AdImpression` and/or `AdClick` models
2. Update the tracking views to capture the new data
3. Update the serializers if needed

### Caching
The module uses Django's cache framework. To customize:
1. Update the cache keys in `AdService`
2. Adjust cache timeouts as needed
3. Implement custom cache backends

## Troubleshooting

### Ads not displaying
- Check that the ad slot is active
- Check that the advertisement is active
- Check that the advertisement's start/end dates are valid
- Check that the ad type has the required content

### Tracking not working
- Ensure the tracking URLs are accessible
- Check that JavaScript is enabled in the browser
- Verify that the ad ID is correct

### Statistics not updating
- Check that impressions and clicks are being tracked
- Verify that the counters are being incremented
- Check for any JavaScript errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure nothing is broken
5. Submit a pull request

## License

This module is part of the shop-template project and is licensed under the same terms.
