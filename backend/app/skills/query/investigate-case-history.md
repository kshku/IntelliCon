---
name: investigate-case-history
description: Get complete history and details of a specific case
triggers:
  - "case details"
  - "investigate case"
  - "case history"
  - "full case"
  - "case summary"
tools_required:
  - sql_query
---
# Investigate Case History

## Steps
1. Look up the case by case number or crime number
2. Retrieve all related records: complainants, victims, accused, arrests
3. Get chargesheet details if available
4. Compile a comprehensive case summary

## Example Queries
- "Show me the full details of case KA-2024-0001"
- "Investigate Cr.No.123/2024"
- "What is the history of case #456?"

## SQL Pattern
```sql
SELECT 
  cm.*, 
  cd.name as complainant_name,
  v.name as victim_name,
  a.name as accused_name,
  asa.act_id, asa.section_id,
  ch.chargesheet_date, ch.investigating_officer
FROM case_master cm
LEFT JOIN complainant_details cd ON cm.case_id = cd.case_id
LEFT JOIN victim v ON cm.case_id = v.case_id
LEFT JOIN accused a ON cm.case_id = a.case_id
LEFT JOIN act_section_association asa ON cm.case_id = asa.case_id
LEFT JOIN chargesheet_details ch ON cm.case_id = ch.case_id
WHERE cm.case_no = 'KA-2024-0001' OR cm.crime_no = 'Cr.No.123/2024'
```
