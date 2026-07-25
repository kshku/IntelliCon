---
name: analyze-chargesheet-outcomes
description: Analyze chargesheet filing patterns and case outcomes
triggers:
  - "chargesheet"
  - "case outcome"
  - "filing rate"
  - "chargesheet analysis"
  - "case resolution"
tools_required:
  - sql_query
---
# Analyze Chargesheet Outcomes

## Steps
1. Use sql_query to find cases with and without chargesheets
2. Calculate chargesheet filing rates by category or district
3. Analyze time from registration to chargesheet
4. Identify patterns in outcomes

## Example Queries
- "What is the chargesheet filing rate for theft cases?"
- "How many cases still need chargesheets?"
- "Average time to file chargesheet by crime type"

## SQL Pattern
```sql
SELECT 
  cc.category_name,
  COUNT(DISTINCT cm.case_id) as total_cases,
  COUNT(DISTINCT ch.chargesheet_id) as chargesheet_count,
  ROUND(COUNT(DISTINCT ch.chargesheet_id)::numeric / 
    COUNT(DISTINCT cm.case_id) * 100, 2) as filing_rate
FROM case_master cm
JOIN case_category cc ON cm.case_category_id = cc.case_category_id
LEFT JOIN chargesheet_details ch ON cm.case_id = ch.case_id
GROUP BY cc.category_name
ORDER BY filing_rate DESC
```
