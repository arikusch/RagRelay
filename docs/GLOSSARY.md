# Glossary

| Term | Meaning |
|---|---|
| worker | a retrieval endpoint profile in the fixture |
| query | an incoming request scored against every worker |
| affinity | the weighted blend of cosine, topic overlap and latency |
| fanout | how many top-ranked workers a query may spread attempts over |
| largest-remainder | the method that splits attempts without rounding drift |
| capacity pressure | attempts used divided by a worker's capacity |
| run_id | the first 16 hex chars of the canonical-input digest |
