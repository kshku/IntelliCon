---
name: find-repeat-offenders
description: Identify individuals who appear as accused in multiple cases
triggers:
  - "repeat offenders"
  - "serial criminals"
  - "multiple cases"
  - "who has been arrested before"
  - "recidivism"
tools_required:
  - sql_query
---
# Find Repeat Offenders

## Steps
1. Use sql_query to find accused persons appearing in multiple cases
2. Group by name and count distinct cases
3. Include case details for context
4. Rank by number of cases

## Example Queries
- "Who are the repeat offenders in our database?"
- "Find people arrested in more than 3 cases"
- "Which accused persons have the most cases?"

## SQL Pattern
```sql
SELECT 
  a.name,
  COUNT(DISTINCT a.case_id) as case_count,
  STRING_AGG(DISTINCT cm.case_no, ', ') as case_numbers
FROM accused a
JOIN case_master cm ON a.case_id = cm.case_id
GROUP BY a.name
HAVING COUNT(DISTINCT a.case_id) > 1
ORDER BY case_count DESC
```
