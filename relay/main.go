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
	return float64(hit) / float64(len(q))
}

// latencyScore maps base latency to a 0..1 preference (lower latency is better).
// urgency sharpens the penalty for slow endpoints.
func latencyScore(baseLat, urgency float64) float64 {
	if baseLat <= 0 {
		return 1
	}
	k := 40.0 * (1.0 + urgency)
	return k / (k + baseLat)
}

func rank(p Profiles) []Ranked {
	var out []Ranked
	for _, q := range p.Queries {
		var rows []Ranked
		for _, w := range p.Workers {
			cos := cosine(q.Vector, w.Vector)
			th := topicOverlap(q.Topics, w.Topics)
			ls := latencyScore(w.BaseLatMS, q.Urgency)
			// Deterministic weighted blend.
			aff := (0.5*cos + 0.3*th + 0.2*ls) * w.Weight
			rows = append(rows, Ranked{
				QueryID:   q.ID,
				WorkerID:  w.ID,
				Region:    w.Region,
				Affinity:  round4(aff),
				Cosine:    round4(cos),
				TopicHit:  round4(th),
				LatScore:  round4(ls),
				BaseLatMS: w.BaseLatMS,
			})
		}
		// Stable ordering: affinity desc, then worker id asc for ties.
		sort.SliceStable(rows, func(i, j int) bool {
			if rows[i].Affinity != rows[j].Affinity {
				return rows[i].Affinity > rows[j].Affinity
			}
			return rows[i].WorkerID < rows[j].WorkerID
		})
		for i := range rows {
			rows[i].Rank = i + 1
		}
		out = append(out, rows...)
	}
	return out
}

func round4(f float64) float64 {
	return math.Round(f*10000) / 10000
}

func main() {
	in := flag.String("in", "", "path to profiles JSON fixture (default stdin)")
	top := flag.Int("top", 0, "limit rows per query (0 = all)")
	pretty := flag.Bool("pretty", false, "pretty-print JSON output")
	flag.Parse()

	var data []byte
	var err error
	if *in == "" {
		data, err = readAll(os.Stdin)
	} else {
		data, err = os.ReadFile(*in)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, "relay: read error:", err)
		os.Exit(1)
	}

	var p Profiles
	if err := json.Unmarshal(data, &p); err != nil {
		fmt.Fprintln(os.Stderr, "relay: parse error:", err)
		os.Exit(1)
	}
	if len(p.Workers) == 0 || len(p.Queries) == 0 {
		fmt.Fprintln(os.Stderr, "relay: fixture must contain workers and queries")
		os.Exit(1)
	}

	rows := rank(p)
	if *top > 0 {
		rows = limitPerQuery(rows, *top)
	}

	enc := json.NewEncoder(os.Stdout)
	if *pretty {
		enc.SetIndent("", "  ")
	}
	if err := enc.Encode(rows); err != nil {
		fmt.Fprintln(os.Stderr, "relay: encode error:", err)
		os.Exit(1)
	}
}

func limitPerQuery(rows []Ranked, top int) []Ranked {
	counts := map[string]int{}
	var out []Ranked
	for _, r := range rows {
		if counts[r.QueryID] >= top {
			continue
		}
		counts[r.QueryID]++
		out = append(out, r)
	}
	return out
}

func readAll(f *os.File) ([]byte, error) {
	buf := make([]byte, 0, 4096)
	tmp := make([]byte, 4096)
	for {
		n, err := f.Read(tmp)
		if n > 0 {
			buf = append(buf, tmp[:n]...)
		}
		if err != nil {
			if err.Error() == "EOF" {
				return buf, nil
			}
			return buf, nil
		}
	}
}
