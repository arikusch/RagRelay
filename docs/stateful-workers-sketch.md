# Stateful worker sketch

Profiles describe scoring only. A `session` key could pin related queries to
the same worker while the rest of the routing stays deterministic.

Open question: whether stickiness belongs in the fixture or the manifest.
