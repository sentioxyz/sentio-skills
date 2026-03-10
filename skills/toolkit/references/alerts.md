# Alerts Notes

## Alert types
- Metrics alerts.
- Log alerts.
- SQL alerts.

## SQL alert requirements
- SQL results must include a time column and a numeric value column.
- Use `$startTime` and `$endTime` placeholders in SQL alerts.

## Conditions
- Column-based: pick an aggregation, operator, and threshold.
- Row-based: trigger when query returns any rows.

## Notifications
- Configure channels such as email, Discord, or Telegram.
- Use message variables to include dynamic data in notifications.

## Scheduling and error handling
- Configure evaluation intervals.
- Optionally notify on errors.
- Optionally send resolved notifications.
