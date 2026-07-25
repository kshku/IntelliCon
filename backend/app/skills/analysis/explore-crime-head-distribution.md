---
name: explore-crime-head-distribution
description: Analyze distribution of crimes across crime heads and sub-heads
triggers:
  - "crime types"
  - "crime distribution"
  - "crime head"
  - "which crimes"
  - "crime breakdown"
tools_required:
  - sql_query
---
# Explore Crime Head Distribution

## Steps
1. Use sql_query to count cases by crime major head
2. Break down by sub-head for detailed view
3. Show percentage distribution
4. Highlight most and least common crime types

## Example Queries
- "What are the most common crime types?"
- "Show distribution of crime heads"
- "Which crime category has the most cases?"

## SQL Pattern
```sql
SELECT 
  ch.head_name,
  COUNT(cm.case_id) as case_count,
  ROUND(COUNT(cm.case_id)::numeric / 
    (SELECT COUNT(*) FROM case_master) * 100, 2) as percentage
FROM case_master cm
JOIN crime_head ch ON cm.crime_major_head_id = ch.crime_head_id
GROUP BY ch.head_name
ORDER BY case_count DESC
```
