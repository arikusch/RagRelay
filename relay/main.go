// Command relay scores and ranks retrieval endpoints for the RagRelay
// simulator. It reads a worker-profile fixture (JSON) plus a query vector and
// emits a deterministic ranking of endpoints by an affinity score.
//
// The scoring model is intentionally transparent and reproducible: given the
// same inputs it always produces the same ordering. It uses only the Go
// standard library.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
	"sort"
	"strings"
)

// Worker describes a retrieval endpoint profile.
type Worker struct {
