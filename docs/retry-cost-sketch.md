# Cost-aware retries

The allocator already reads latency envelopes from the fixture. A weighted
cost per attempt (affinity x latency envelope) would keep budgets honest when
one region is under pressure.

No manifest schema change needed - the weights live in the fixture.
