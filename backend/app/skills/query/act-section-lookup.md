---
name: act-section-lookup
description: Find which acts and sections apply to specific crime types
triggers:
  - "which act"
  - "applicable sections"
  - "legal sections"
  - "act for crime"
  - "section lookup"
tools_required:
  - sql_query
---
# Act Section Lookup

## Steps
1. Use sql_query to find crime heads and their associated acts/sections
2. Map crime types to applicable legal provisions
3. Provide context on what each section covers

## Example Queries
- "Which sections apply to theft cases?"
- "What act is used for murder cases?"
- "Show all sections for crime head 'Robbery'"

## SQL Pattern
```sql
SELECT 
  ch.head_name,
  a.act_name,
  s.section_number,
  s.description
FROM crime_head ch
JOIN crime_head_act_section chas ON ch.crime_head_id = chas.crime_head_id
JOIN act a ON chas.act_id = a.act_id
JOIN section s ON chas.section_id = s.section_id
WHERE ch.head_name ILIKE '%theft%'
ORDER BY a.act_name, s.section_number
```
