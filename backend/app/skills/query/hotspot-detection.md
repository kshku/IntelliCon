---
name: hotspot-detection
description: Identify crime hotspots based on geographic clustering of cases
triggers:
  - "crime hotspots"
  - "where are crimes"
  - "crime locations"
  - "geographic analysis"
  - "hotspot map"
tools_required:
  - sql_query
---
# Hotspot Detection

## Steps
1. Use sql_query to get case locations (latitude, longitude)
2. Group by police station or district for clustering
3. Identify areas with highest case concentrations
4. Present as ranked hotspots

## Example Queries
- "Where are the crime hotspots in Bengaluru?"
- "Show areas with most crimes by location"
- "Which police station area has the highest crime rate?"

## SQL Pattern
```sql
SELECT 
  u.unit_name,
  d.district_name,
  COUNT(cm.case_id) as case_count,
  AVG(cm.latitude) as avg_lat,
  AVG(cm.longitude) as avg_lng
FROM case_master cm
JOIN unit u ON cm.police_station_id = u.unit_id
JOIN district d ON u.district_id = d.district_id
WHERE cm.latitude IS NOT NULL AND cm.longitude IS NOT NULL
GROUP BY u.unit_name, d.district_name
HAVING COUNT(cm.case_id) > 5
ORDER BY case_count DESC
```
