# Ads API Documentation

## Overview
The Ads API provides endpoints for managing advertisements, ad slots, tracking impressions and clicks, and retrieving statistics.

## Authentication
Most endpoints require admin authentication. Use token authentication or session authentication.

## Base URL
All API endpoints are prefixed with `/api/v1/ads/`

---

## Ad Slot Endpoints

### List and Create Ad Slots
- **URL**: `/api/v1/ads/slots/`
- **Method**: `GET` (list), `POST` (create)
- **Permissions**: Admin only
- **Query Parameters**:
  - `q`: Search term (name, code, description)
  - `is_active`: Filter by active status
  - `is_responsive`: Filter by responsive status

**Request (POST)**:
```json
{
    "name": "Header Banner",
    "code": "header_banner",
    "description": "Banner in the header",
    "width": 1200,
    "height": 200,
    "is_responsive": false,
    "is_active": true
}
```

**Response (GET)**:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "Header Banner",
            "code": "header_banner",
            "description": "Banner in the header",
            "width": 1200,
            "height": 200,
            "is_responsive": false,
            "is_active": true,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        }
    ]
}
```

### Retrieve, Update, or Delete Ad Slot
- **URL**: `/api/v1/ads/slots/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), `PATCH` (partial update), `DELETE` (delete)
- **Permissions**: Admin only

---

## Advertisement Endpoints

### List and Create Advertisements
- **URL**: `/api/v1/ads/advertisements/`
- **Method**: `GET` (list), `POST` (create)
- **Permissions**: Admin only
- **Query Parameters**:
  - `q`: Search term (name, title, description)
  - `slot_id`: Filter by slot ID
  - `slot_code`: Filter by slot code
  - `ad_type`: Filter by ad type (image, html, script, video)
  - `is_active`: Filter by active status
  - `priority`: Filter by priority
  - `priority__gte`: Filter by minimum priority
  - `priority__lte`: Filter by maximum priority
  - `date_from`: Filter by start date
  - `date_to`: Filter by end date

**Request (POST)**:
```json
{
    "name": "Summer Sale",
    "slot_id": "uuid",
    "ad_type": "image",
    "title": "Summer Sale Banner",
    "description": "Special summer sale",
    "priority": 10,
    "url": "https://example.com/sale",
    "target": "_blank",
    "is_active": true
}
```

**Response (GET)**:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "Summer Sale",
            "slot": {
                "id": "uuid",
                "name": "Header Banner",
                "code": "header_banner",
                ...
            },
            "ad_type": "image",
            "title": "Summer Sale Banner",
            "description": "Special summer sale",
            "priority": 10,
            "url": "https://example.com/sale",
            "target": "_blank",
            "is_active": true,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
            "impression_count": 0,
            "click_count": 0
        }
    ]
}
```

### Retrieve, Update, or Delete Advertisement
- **URL**: `/api/v1/ads/advertisements/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), `PATCH` (partial update), `DELETE` (delete)
- **Permissions**: Admin only

---

## Ad Display Endpoints

### Display Ad for Slot
- **URL**: `/api/v1/ads/display/{slot_code}/`
- **Method**: `GET`
- **Permissions**: Public
- **Response**: Returns ad data for display

**Response**:
```json
{
    "id": "uuid",
    "name": "Summer Sale",
    "title": "Summer Sale Banner",
    "description": "Special summer sale",
    "ad_type": "image",
    "image_url": "https://example.com/media/ads/summer_sale.jpg",
    "html_content": null,
    "script_content": null,
    "video_url": null,
    "video_embed_code": null,
    "url": "https://example.com/sale",
    "target": "_blank",
    "priority": 10,
    "is_active": true
}
```

### Display Responsive Ad
- **URL**: `/api/v1/ads/display/{slot_code}/{width}/{height}/`
- **Method**: `GET`
- **Permissions**: Public
- **Response**: Returns ad data with dimensions

---

## Tracking Endpoints

### Track Ad Impression
- **URL**: `/api/v1/ads/track/impression/{ad_id}/`
- **Method**: `POST`
- **Permissions**: Public
- **Response**: 201 Created on success

### Track Ad Click
- **URL**: `/api/v1/ads/track/click/{ad_id}/`
- **Method**: `POST`
- **Permissions**: Public
- **Response**: 201 Created on success

---

## Statistics Endpoints

### Get Advertisement Statistics
- **URL**: `/api/v1/ads/stats/{ad_id}/`
- **Method**: `GET`
- **Permissions**: Admin only
- **Response**:
```json
{
    "id": "uuid",
    "name": "Summer Sale",
    "title": "Summer Sale Banner",
    "ad_type": "image",
    "impression_count": 100,
    "click_count": 10,
    "ctr": 10.0,
    "conversion_rate": 0
}
```

### Get Ad Slot Statistics
- **URL**: `/api/v1/ads/stats/slot/{slot_code}/`
- **Method**: `GET`
- **Permissions**: Admin only
- **Response**:
```json
{
    "id": "uuid",
    "name": "Header Banner",
    "code": "header_banner",
    "total_impressions": 1000,
    "total_clicks": 100,
    "total_ads": 5,
    "active_ads": 3,
    "average_ctr": 10.0
}
```

### Get Overall Statistics
- **URL**: `/api/v1/ads/stats/`
- **Method**: `GET`
- **Permissions**: Admin only
- **Response**:
```json
{
    "total_ads": 10,
    "active_ads": 8,
    "total_impressions": 5000,
    "total_clicks": 500,
    "overall_ctr": 10.0,
    "top_ads": [
        {
            "id": "uuid",
            "name": "Best Ad",
            "title": "Best Ad Title",
            "ad_type": "image",
            "impression_count": 1000,
            "click_count": 200,
            "ctr": 20.0
        }
    ]
}
```

---

## Report Endpoints

### Get Impression Report
- **URL**: `/api/v1/ads/reports/impressions/`
- **Method**: `GET`
- **Permissions**: Admin only
- **Query Parameters**:
  - `date_from`: Start date
  - `date_to`: End date
  - `slot_code`: Filter by slot code
- **Response**: Array of date/count objects

### Get Click Report
- **URL**: `/api/v1/ads/reports/clicks/`
- **Method**: `GET`
- **Permissions**: Admin only
- **Query Parameters**: Same as impression report
- **Response**: Array of date/count objects

### Get Performance Report
- **URL**: `/api/v1/ads/reports/performance/`
- **Method**: `GET`
- **Permissions**: Admin only
- **Query Parameters**:
  - `date_from`: Start date
  - `date_to`: End date
- **Response**: Array of ad performance data

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Resource deleted
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

API endpoints may be rate limited. Check response headers for:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

---

## Versioning

The current API version is `v1`. Future versions may be released with breaking changes.
