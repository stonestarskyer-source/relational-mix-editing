# Relational mix editing

Research code and protocols accompanying **Musical Relationship Constraints in AI-Assisted Local Mix Editing** (manuscript v1.9).

The repository provides [S1: signal verification](docs/S1_signal_verification.md) and [S2: candidate selection and listening protocol](docs/S2_listening_protocol.md) as readable documents. The technical baseline originated in the v1.8 materials; the manuscript title and document mapping follow the supplied v1.9 draft.

The two original scripts are preserved without changes. The DSP example uses deterministic synthetic diagnostic signals, not recorded vocals, bass or songs. Pedalboard compression does not reproduce REAPER's ReaComp implementation. No human listening study or end-to-end AI mixing experiment has been completed in these materials.

```bash
mkdir -p output
python3 code/candidate_protocol.py --output output/analytical_candidates.json
python3 -m unittest discover -s tests -v
```

For the DSP example, create a separate Python 3.13 environment and install `code/requirements.txt`, then run `python code/run_dsp_example.py --out output/dsp`. Historical and new results are kept separately. Never overwrite reference records. Scripts may overwrite their own output files: use a fresh output directory.

The candidate script covers a fixed two-track analytical example and a single-target scoring helper, not a general DAW controller, EQ rendering system or multi-target listening evaluator. See [implementation boundaries](docs/provenance.md).

Public availability is distinct from a reuse license. No project-wide license has been chosen by the author; see [licensing status](docs/licensing.md). The manuscript and private review material are excluded.
