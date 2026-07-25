---
name: trace-accused-network
description: Find all connections between an accused person and other individuals across cases
triggers:
  - "who is connected to"
  - "network of"
  - "links between"
  - "connections of"
  - "accused network"
tools_required:
  - graph_query
  - sql_query
---
# Trace Accused Network

## Steps
1. Identify the accused by name or ID using sql_query
2. Query the graph for all direct connections (shared cases)
3. Expand to 2-hop connections
4. Format results as a network summary

## Example Queries
- "Who is connected to John Doe across all cases?"
- "Show the network of accused person #123"
- "Find all links between Ravi and other suspects"

## Approach
1. First, find the accused in the accused table
2. Find all cases they are associated with
3. For each case, find other accused persons
4. Build a connection graph: person → case → person
5. Optionally expand to second-degree connections
