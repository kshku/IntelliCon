---
name: generate-case-report
description: Generate a formatted report for a specific case or investigation
triggers:
  - "generate report"
  - "case report"
  - "investigation report"
  - "create report"
  - "export case"
tools_required:
  - sql_query
---
# Generate Case Report

## Steps
1. Use sql_query to gather all case details
2. Structure information into report sections
3. Include timeline, participants, and legal sections
4. Format for readability

## Example Queries
- "Generate a report for case KA-2024-0001"
- "Create an investigation summary for Cr.No.123/2024"
- "Export case details for the supervisor"

## Report Structure
1. **Case Overview**: Case number, crime number, dates, location
2. **Parties Involved**: Complainants, victims, accused
3. **Timeline**: Key dates (registration, arrest, chargesheet)
4. **Legal Sections**: Acts and sections applied
5. **Current Status**: Case status, court assignment
6. **Investigating Officer**: Officer details
