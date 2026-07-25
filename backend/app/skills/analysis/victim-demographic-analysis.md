---
name: victim-demographic-analysis
description: Analyze victim demographics including age, gender, caste, and religion
triggers:
  - "victim demographics"
  - "victim analysis"
  - "who are the victims"
  - "victim profile"
  - "demographics"
tools_required:
  - sql_query
---
# Victim Demographic Analysis

## Steps
1. Use sql_query to aggregate victim data
2. Break down by age group, gender, caste, religion
3. Cross-reference with crime types
4. Present demographic insights

## Example Queries
- "What is the age distribution of victims?"
- "Show victim demographics by gender"
- "Which crime types affect which demographics?"

## SQL Pattern
```sql
SELECT 
  v.gender,
  CASE 
    WHEN v.age < 18 THEN 'Minor'
    WHEN v.age BETWEEN 18 AND 30 THEN '18-30'
    WHEN v.age BETWEEN 31 AND 50 THEN '31-50'
    ELSE '50+'
  END as age_group,
  COUNT(*) as victim_count
FROM victim v
GROUP BY v.gender, age_group
ORDER BY victim_count DESC
```
