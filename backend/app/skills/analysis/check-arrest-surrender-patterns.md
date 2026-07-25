---
name: check-arrest-surrender-patterns
description: Analyze patterns in arrests versus surrenders across cases
triggers:
  - "arrest vs surrender"
  - "arrest patterns"
  - "surrender rate"
  - "how many arrested"
  - "arrest analysis"
tools_required:
  - sql_query
---
# Check Arrest vs Surrender Patterns

## Steps
1. Use sql_query to count arrests and surrenders
2. Compare by district, crime type, or time period
3. Calculate surrender rates
4. Identify patterns

## Example Queries
- "How many arrests vs surrenders were there last month?"
- "What is the surrender rate for violent crimes?"
- "Which police station has the most arrests?"

## SQL Pattern
```sql
SELECT 
  u.unit_name,
  COUNT(CASE WHEN ar.arrest_date IS NOT NULL THEN 1 END) as arrests,
  COUNT(CASE WHEN ar.surrender_date IS NOT NULL THEN 1 END) as surrenders
FROM arrest_surrender ar
JOIN case_master cm ON ar.case_id = cm.case_id
JOIN unit u ON cm.police_station_id = u.unit_id
GROUP BY u.unit_name
ORDER BY arrests DESC
```
