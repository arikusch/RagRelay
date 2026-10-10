# Fixture key ordering

The manifest hash runs over a canonicalized fixture, so re-ordering keys in
the JSON input does not change run_id. Keep fixtures human-readable - the
canonicalization happens at load time.
