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
	Region    string  `json:"region"`
	Affinity  float64 `json:"affinity"`
	Cosine    float64 `json:"cosine"`
	TopicHit  float64 `json:"topic_hit"`
	LatScore  float64 `json:"latency_score"`
	BaseLatMS float64 `json:"base_latency_ms"`
	Rank      int     `json:"rank"`
}

func cosine(a, b []float64) float64 {
	n := len(a)
	if len(b) < n {
		n = len(b)
	}
	var dot, na, nb float64
	for i := 0; i < n; i++ {
		dot += a[i] * b[i]
		na += a[i] * a[i]
		nb += b[i] * b[i]
	}
	if na == 0 || nb == 0 {
		return 0
	}
	return dot / (math.Sqrt(na) * math.Sqrt(nb))
}

func topicOverlap(q, w []string) float64 {
	if len(q) == 0 {
		return 0
	}
	set := make(map[string]struct{}, len(w))
	for _, t := range w {
		set[strings.ToLower(t)] = struct{}{}
	}
	hit := 0
	for _, t := range q {
		if _, ok := set[strings.ToLower(t)]; ok {
			hit++
		}
	}
