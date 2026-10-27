// Calls the Go library Robusto (github.com/victoralmeida428/estatistica_robusta, tag v0.2.0, commit a0fca48)
// on the 200 data sets of compare.py. Robusto is not part of this repository and has no stated license;
// only its outputs are stored here. Run: see README.md.
package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/victoralmeida428/estatistica_robusta/robusto"
)

func main() {
	var sets [][]float64
	var scales [][]float64
	b, _ := os.ReadFile("sets.json")
	json.Unmarshal(b, &sets)
	b, _ = os.ReadFile("scales.json")
	json.Unmarshal(b, &scales)
	out := []map[string]any{}
	for i, x := range sets {
		s := robusto.New(x)
		qhLoc, qScale := s.QMethod()
		_, qnScale := s.Qn()
		aLoc, aScale := s.AlgorithmA(true)
		h := []float64{s.HampelMean(scales[i][0]), s.HampelMean(scales[i][1]), s.HampelMean(scales[i][2])}
		out = append(out, map[string]any{"q_scale": qScale, "qhampel_loc": qhLoc, "qn_scale": qnScale,
			"a_loc": aLoc, "a_scale": aScale, "hampel_at_q_made_qn": h})
	}
	j, _ := json.Marshal(out)
	fmt.Println(string(j))
}
