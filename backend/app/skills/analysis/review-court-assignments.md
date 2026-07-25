---
name: review-court-assignments
description: Analyze case distribution and patterns across courts
triggers:
  - "court assignments"
  - "court distribution"
  - "which court"
  - "court workload"
  - "court analysis"
tools_required:
  - sql_query
---
# Review Court Assignments

## Steps
1. Use sql_query to count cases by court
2. Break down by court type
3. Show average case age per court
4. Identify workload distribution

## Example Queries
- "How many cases are assigned to each court?"
- "What is the workload of district courts vs sessions courts?"
- "Which court has the most pending cases?"

## SQL Pattern
```sql
SELECT 
  c.court_name,
  c.court_type,
  COUNT(cm.case_id) as case_count,
  COUNT(CASE WHEN csm.status_name = 'Pending' THEN 1 END) as pending_count
FROM case_master cm
JOIN court c ON cm.court_id = c.court_id
LEFT JOIN case_status_master csm ON cm.case_status_id = csm.case_status_id
GROUP BY c.court_name, c.court_type
ORDER BY case_count DESC
```
