---
name: crime-statistics-by-district
description: Query crime counts and breakdowns by district, police station, or unit
triggers:
  - "crime statistics"
  - "how many cases in"
  - "crime count by"
  - "cases in district"
  - "police station stats"
tools_required:
  - sql_query
---
# Crime Statistics by District

## Steps
1. Use sql_query to count cases grouped by district or police station
2. Join case_master with unit and district tables for location data
3. Optionally filter by date range, case category, or crime type
4. Present results as a ranked list with counts

## Example Queries
- "How many theft cases were reported in Mangaluru district?"
- "Show crime statistics for each police station in Bengaluru"
- "Which district has the most murder cases this year?"

## SQL Pattern
```sql
SELECT d.district_name, u.unit_name, COUNT(cm.case_id) as case_count
FROM case_master cm
JOIN unit u ON cm.police_station_id = u.unit_id
JOIN district d ON u.district_id = d.district_id
WHERE cm.crime_registered_date LIKE '2024%'
GROUP BY d.district_name, u.unit_name
ORDER BY case_count DESC
```
