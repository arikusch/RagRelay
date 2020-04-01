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
	ID        string    `json:"id"`
	Region    string    `json:"region"`
	Topics    []string  `json:"topics"`
	Weight    float64   `json:"weight"`
	BaseLatMS float64   `json:"base_latency_ms"`
	Capacity  int       `json:"capacity"`
	Vector    []float64 `json:"vector"`
}

// Query describes an incoming retrieval request.
type Query struct {
	ID      string    `json:"id"`
	Topics  []string  `json:"topics"`
	Vector  []float64 `json:"vector"`
	Urgency float64   `json:"urgency"`
}

// Profiles is the fixture root document.
type Profiles struct {
	Workers []Worker `json:"workers"`
	Queries []Query  `json:"queries"`
}

// Ranked is a single scored endpoint row.
type Ranked struct {
	QueryID   string  `json:"query_id"`
	WorkerID  string  `json:"worker_id"`
