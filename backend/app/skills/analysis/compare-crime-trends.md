---
name: compare-crime-trends
description: Compare crime trends across different time periods (month-over-month, year-over-year)
triggers:
  - "compare trends"
  - "crime trends"
  - "month over month"
  - "year over year"
  - "trend comparison"
  - "how has crime changed"
tools_required:
  - sql_query
---
# Compare Crime Trends

## Steps
1. Use sql_query to aggregate case counts by time period
2. Group by month or year as appropriate
3. Calculate percentage changes between periods
4. Highlight significant increases or decreases

## Example Queries
- "Compare theft cases between 2023 and 2024"
- "Show monthly crime trends for the last year"
- "Which crime types increased the most this year?"

## SQL Pattern
```sql
SELECT 
  SUBSTRING(crime_registered_date, 1, 7) as month,
  COUNT(*) as case_count
FROM case_master
WHERE crime_registered_date LIKE '2024%'
GROUP BY month
ORDER BY month
```
