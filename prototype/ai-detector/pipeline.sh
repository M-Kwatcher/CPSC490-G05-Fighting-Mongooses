#!/usr/bin/env bash
# pipeline.sh
# Builds and trains the model(s) for the specified whale
# with the settings best suited to them
# because this is WAY easier


set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALL_SPECIES="humpback blue right"

usage() {
cat <<'EOF'
Usage: run_pipeline.sh --species humpback|blue|right|all [options]

Expected folder layout under --data (default ./data) for real recordings:
  boat_raw/            vessel recordings (shared by all species)
  ambient_raw/         whale-free quiet-water recordings (shared)
  <species>_raw/       recordings containing that species' calls
  <species>_calls.csv  annotations: file,start_s,end_s   (file relative to <species>_raw/)
Outputs go to <data>/<species>/ (windows, and eval if --eval) and models/model_<species>.pt.

Options:
  --species NAME        humpback | blue | right | all   (required)
  --data DIR            base data folder                      [data]
  --boat_src DIR        boat recordings (e.g. on a USB)       [<data>/boat_raw]
  --ambient_src DIR     quiet-water recordings                [<data>/ambient_raw]
  --whale_src DIR       this species' recordings              [<data>/<species>_raw]
  --annotations FILE    this species' annotation CSV          [<data>/<species>_calls.csv]
  --ambient_exclude F   CSV of spans to skip in ambient audio (e.g. known calls)
  --models DIR          where to save model files             [models]
  --epochs N            training epochs                       [30]
  --synth_per_call N    boat-noise mixes per annotated call   [3]
  --synthetic           generate synthetic stand-in audio first (pipeline test only)
  --no_cross_negatives  do not use the other species' calls as extra negatives
  --eval                also run evaluate_detector.py after training (off by default)
  --eval_split S        val | test, used by --eval              [val]
                        (val was used to pick the best epoch and threshold, so it is
                        optimistic; use test once, at the very end)
  --python CMD          python command                        [python3]
  --dry_run             print the commands without running them
  -h, --help            show this help
EOF
}

die() { echo "error: $*" >&2; exit 1; }

# ---- defaults ---------------------------------------------------------------
SPECIES=""; DATA="data"; BOAT_SRC=""; AMB_SRC=""; WHALE_SRC=""; ANN=""; AMB_EXCLUDE=""
MODELS="models"; EPOCHS=30; SYNTH_PER_CALL=3; SYNTHETIC=0; CROSS=1; SKIP_EVAL=1
EVAL_SPLIT="val"; PYTHON="python3"; DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --species)            SPECIES="$2"; shift 2 ;;
    --data)               DATA="$2"; shift 2 ;;
    --boat_src)           BOAT_SRC="$2"; shift 2 ;;
    --ambient_src)        AMB_SRC="$2"; shift 2 ;;
    --whale_src)          WHALE_SRC="$2"; shift 2 ;;
    --annotations)        ANN="$2"; shift 2 ;;
    --ambient_exclude)    AMB_EXCLUDE="$2"; shift 2 ;;
    --models)             MODELS="$2"; shift 2 ;;
    --epochs)             EPOCHS="$2"; shift 2 ;;
    --synth_per_call)     SYNTH_PER_CALL="$2"; shift 2 ;;
    --synthetic)          SYNTHETIC=1; shift ;;
    --no_cross_negatives) CROSS=0; shift ;;
    --eval)               SKIP_EVAL=0; shift ;;
    --eval_split)         EVAL_SPLIT="$2"; shift 2 ;;
    --python)             PYTHON="$2"; shift 2 ;;
    --dry_run)            DRY_RUN=1; shift ;;
    -h|--help)            usage; exit 0 ;;
    *)                    usage; die "unknown option: $1" ;;
  esac
done

[ -n "$SPECIES" ] || { usage; die "--species is required"; }
case "$EVAL_SPLIT" in val|test) ;; *) die "--eval_split must be val or test" ;; esac

run() {
  echo "+ $*"
  if [ "$DRY_RUN" -eq 0 ]; then "$@"; fi
}

# ---- per-species settings (the same values go to EVERY script) --------------
# These are starting points based on typical call frequencies and durations; tune them
# against your own recordings.
set_settings() {
  case "$1" in
    humpback) SR=8000; WIN=4;  HOP=2;   FMIN=20; FMAX=3500; NMELS=64 ;;  # songs/calls ~100 Hz-4 kHz, 1-4 s units
    blue)     SR=1000; WIN=20; HOP=10;  FMIN=10; FMAX=200;  NMELS=32 ;;  # ~15-40 Hz Hz B calls (10-20 s), D calls <100 Hz
    right)    SR=1000; WIN=5;  HOP=2.5; FMIN=20; FMAX=400;  NMELS=64 ;;  # upcalls ~100-200 Hz, ~1 s
    *) die "unknown species '$1' (use humpback, blue, right or all)" ;;
  esac
}

has_audio() {   # does the folder contain at least one audio file?
  local first
  first=$(find "$1" -type f \( -iname '*.wav' -o -iname '*.flac' -o -iname '*.mp3' -o -iname '*.ogg' \) 2>/dev/null | head -n 1 || true)
  [ -n "$first" ]
}

need_audio() {  # need_audio DIR LABEL
  if [ "$DRY_RUN" -eq 1 ]; then return 0; fi
  [ -d "$1" ] || die "$2 folder not found: $1  (use --data, or --$3 to point at it)"
  has_audio "$1" || die "no audio files (.wav/.flac/.mp3/.ogg) found under $1"
}

# ---- one species ------------------------------------------------------------
run_species() {
  local sp="$1" o
  set_settings "$sp"
  local W="$DATA/$sp" MODEL="$MODELS/model_$sp.pt"
  local others=""
  for o in $ALL_SPECIES; do
    if [ "$o" != "$sp" ]; then others="$others $o"; fi
  done

  echo
  echo "=================================================================="
  echo " Species: $sp   (sr=$SR win=$WIN hop=$HOP fmin=$FMIN fmax=$FMAX n_mels=$NMELS)"
  echo "=================================================================="

  # Resolve where the raw audio comes from
  local BOAT_DIR="${BOAT_SRC:-$DATA/boat_raw}" AMB_DIR="${AMB_SRC:-$DATA/ambient_raw}"
  local WHALE_DIR="${WHALE_SRC:-$DATA/${sp}_raw}" ANN_FILE="${ANN:-$DATA/${sp}_calls.csv}"
  local SYN="$DATA/synthetic_$sp"

  if [ "$SYNTHETIC" -eq 1 ]; then
    echo "[0] Generating synthetic stand-in audio at sr=$SR (all sources share this rate)"
    BOAT_DIR="$SYN/boat_raw"; AMB_DIR="$SYN/ambient_raw"
    WHALE_DIR="$SYN/${sp}_raw"; ANN_FILE="$SYN/${sp}_calls.csv"
    run "$PYTHON" "$SCRIPT_DIR/generate_synthetic_calls.py" boat    --files 20 --duration 120 --sr "$SR" --seed 11 --out "$BOAT_DIR"
    run "$PYTHON" "$SCRIPT_DIR/generate_synthetic_calls.py" ambient --files 20 --duration 120 --sr "$SR" --seed 12 --out "$AMB_DIR"
    run "$PYTHON" "$SCRIPT_DIR/generate_synthetic_calls.py" whale --species "$sp" --files_per_species 12 \
        --duration 90 --sr "$SR" --seed 13 --out "$WHALE_DIR" --annotations "$ANN_FILE"
    if [ "$CROSS" -eq 1 ]; then
      for o in $others; do
        run "$PYTHON" "$SCRIPT_DIR/generate_synthetic_calls.py" whale --species "$o" --files_per_species 8 \
            --duration 90 --sr "$SR" --seed 14 --out "$SYN/${o}_raw" --annotations "$SYN/${o}_calls.csv"
      done
    fi
  else
    need_audio "$BOAT_DIR" "boat recordings" boat_src
    need_audio "$AMB_DIR" "ambient (quiet water) recordings" ambient_src
    need_audio "$WHALE_DIR" "$sp recordings" whale_src
  fi

  local ANN_ARGS=()
  if [ "$DRY_RUN" -eq 1 ] || [ -f "$ANN_FILE" ]; then
    ANN_ARGS=(--annotations "$ANN_FILE")
  else
    echo "[warn] annotation file not found: $ANN_FILE"
    echo "       treating every file in $WHALE_DIR as one clean call clip"
  fi

  echo "[1/4] Boat-noise class"
  run "$PYTHON" "$SCRIPT_DIR/boat_noise_class.py" --src "$BOAT_DIR" --out "$W/boat" \
      --sr "$SR" --win "$WIN" --hop "$HOP" --n_mels "$NMELS" --fmin "$FMIN" --fmax "$FMAX"

  echo "[2/4] $sp call class (natural windows + calls mixed into the boat windows)"
  run "$PYTHON" "$SCRIPT_DIR/whale_noise_class.py" --src "$WHALE_DIR" "${ANN_ARGS[@]}" \
      --boat "$W/boat" --out "$W/whale" --sr "$SR" --win "$WIN" --n_mels "$NMELS" \
      --fmin "$FMIN" --fmax "$FMAX" --synth_per_call "$SYNTH_PER_CALL"

  echo "[3/4] Ambient-water class"
  local AMB_ARGS=()
  if [ -n "$AMB_EXCLUDE" ]; then AMB_ARGS=(--exclude "$AMB_EXCLUDE"); fi
  run "$PYTHON" "$SCRIPT_DIR/ambient_water_class.py" --src "$AMB_DIR" --out "$W/ambient" \
      --sr "$SR" --win "$WIN" --hop "$HOP" --n_mels "$NMELS" --fmin "$FMIN" --fmax "$FMAX" "${AMB_ARGS[@]}"

  # Other species' calls become extra NEGATIVES at THIS species' settings, so the model
  # learns that they are not its target.
  local EXTRA=("$W/ambient")
  if [ "$CROSS" -eq 1 ]; then
    for o in $others; do
      local O_DIR O_ANN
      if [ "$SYNTHETIC" -eq 1 ]; then O_DIR="$SYN/${o}_raw"; O_ANN="$SYN/${o}_calls.csv"
      else O_DIR="$DATA/${o}_raw"; O_ANN="$DATA/${o}_calls.csv"; fi
      if [ "$DRY_RUN" -eq 1 ] || { [ -d "$O_DIR" ] && [ -f "$O_ANN" ] && has_audio "$O_DIR"; }; then
        echo "      adding $o calls as extra negatives"
        run "$PYTHON" "$SCRIPT_DIR/whale_noise_class.py" --src "$O_DIR" --annotations "$O_ANN" \
            --out "$W/neg_$o" --sr "$SR" --win "$WIN" --n_mels "$NMELS" \
            --fmin "$FMIN" --fmax "$FMAX" --synth_per_call 0
        # rename so the group is not confused with the positive 'whale_call' class
        if [ "$DRY_RUN" -eq 0 ]; then
          for s in train val test; do
            if [ -f "$W/neg_$o/whale_call_$s.npz" ]; then
              mv "$W/neg_$o/whale_call_$s.npz" "$W/neg_$o/${o}_whale_$s.npz"
            fi
          done
        else
          echo "+ (rename $W/neg_$o/whale_call_<split>.npz -> ${o}_whale_<split>.npz)"
        fi
        EXTRA+=("$W/neg_$o")
      else
        echo "      (no $o data at $O_DIR with $O_ANN; skipping it as a negative)"
      fi
    done
  fi

  echo "[4/4] Training -> $MODEL"
  if [ "$DRY_RUN" -eq 0 ]; then mkdir -p "$MODELS"; fi
  run "$PYTHON" "$SCRIPT_DIR/whale_detector.py" train --boat "$W/boat" --whale "$W/whale" \
      --extra_neg "${EXTRA[@]}" --out "$MODEL" --sr "$SR" --win "$WIN" --n_mels "$NMELS" \
      --fmin "$FMIN" --fmax "$FMAX" --epochs "$EPOCHS"

  if [ "$SKIP_EVAL" -eq 0 ]; then
    echo "[eval] evaluate_detector.py on the $EVAL_SPLIT split"
    if ! run "$PYTHON" "$SCRIPT_DIR/evaluate_detector.py" --model "$MODEL" --boat "$W/boat" \
        --whale "$W/whale" --extra_neg "${EXTRA[@]}" --split "$EVAL_SPLIT" --out "$W/eval"; then
      echo "[eval] one or more pass/fail checks did not pass (see $W/eval/results.json)"
    fi
  fi

  echo
  echo "Done: $sp. Model: $MODEL"
  echo "  detect : $PYTHON $SCRIPT_DIR/whale_detector.py detect --model $MODEL --audio recording.wav"
  echo "  live   : $PYTHON $SCRIPT_DIR/live_detector.py --model $MODEL --device <id>"
  if [ "$SYNTHETIC" -eq 1 ]; then
    echo "  NOTE: this model was trained on SYNTHETIC audio. It tests the pipeline, not real whales."
  fi
}

# ---- main -------------------------------------------------------------------
if [ "$SPECIES" = "all" ]; then
  for s in $ALL_SPECIES; do run_species "$s"; done
else
  run_species "$SPECIES"
fi
