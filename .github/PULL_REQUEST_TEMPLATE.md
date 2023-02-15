# Pull request

## What does this change?

<!-- One or two sentences. Link the issue if one exists: "Fixes #12". -->

## Checklist

- [ ] `python -m compileall ragrelay` passes
- [ ] `python -m pytest tests/ -o addopts=""` passes
- [ ] `cd relay && go build ./... && go vet ./...` passes (if the Go side is touched)
- [ ] CLI flags, exit codes, and manifest fields are unchanged (or the change is
