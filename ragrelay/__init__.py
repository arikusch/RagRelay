"""RagRelay — a deterministic retrieval-routing simulator.

The package scores incoming queries against worker profiles, allocates
retrieval attempts across endpoints, summarizes route distribution and
latency, and writes reproducible run manifests.

Public API:
    load_profiles   -- parse a profiles fixture into dataclasses
    score_query     -- affinity score for one query against one worker
