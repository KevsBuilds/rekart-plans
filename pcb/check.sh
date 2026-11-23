#!/usr/bin/env bash
# Run KiCad checks (ERC, DRC, BOM, netlist) for the boards under pcb/.
#
# Usage: pcb/check.sh [board-dir]
#   no argument: every pcb/*/ folder that has a .kicad_pro
#   board-dir:   a path, or just the folder name under pcb/ (e.g. ELEC-control-board)
#
# DRC is skipped (shown as "-") while the .kicad_pcb has no Edge.Cuts outline.
# Writes <board>/reports/{erc,drc}.{json,rpt}, bom.csv, netlist.net, <board>.pdf (git-ignored).
# Exit 0: no error-severity violations (warnings are allowed). Exit 1: any error,
# or kicad-cli itself failed. Needs: KiCad 10 Flatpak (org.kicad.KiCad), jq.
set -euo pipefail

KICAD="flatpak run --command=kicad-cli org.kicad.KiCad"
PCB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

die() { echo "check.sh: $*" >&2; exit 1; }

command -v jq >/dev/null || die "jq not found (install: sudo apt install -y jq)"
# shellcheck disable=SC2086  # KICAD is a command line, word splitting intended
ver="$($KICAD version 2>/dev/null)" || die "kicad-cli not runnable via: $KICAD"
[[ "$ver" == 10.* ]] || die "need KiCad 10.x, got '$ver'"

# Run kicad-cli; exit 0 (clean) and 5 (violations found) are both fine.
# Anything else is a real failure: show its output and return 1.
kicad() {
  local log rc=0
  log="$(mktemp)"
  # shellcheck disable=SC2086
  $KICAD "$@" >"$log" 2>&1 || rc=$?
  if [[ $rc -ne 0 && $rc -ne 5 ]]; then
    echo "  kicad-cli $1 $2 failed (exit $rc):" >&2
    sed 's/^/    /' "$log" >&2
    rm -f "$log"; return 1
  fi
  rm -f "$log"
}

ERC_ERR='[.sheets[]?.violations[]? | select(.severity == "error")] | length'
ERC_WARN='[.sheets[]?.violations[]? | select(.severity == "warning")] | length'
DRC_ALL='(.violations // []) + (.unconnected_items // []) + (.schematic_parity // [])'
DRC_ERR="[$DRC_ALL | .[] | select(.severity == \"error\")] | length"
DRC_WARN="[$DRC_ALL | .[] | select(.severity == \"warning\")] | length"

# Which boards to check
boards=()
if [[ $# -gt 0 ]]; then
  if [[ -d "$1" ]]; then boards=("$(cd "$1" && pwd)")
  elif [[ -d "$PCB_DIR/$1" ]]; then boards=("$PCB_DIR/$1")
  else die "no such board folder: $1"; fi
else
  for d in "$PCB_DIR"/*/; do
    d="${d%/}"
    if compgen -G "$d/*.kicad_pro" >/dev/null; then boards+=("$d")
    else echo "SKIP $(basename "$d"): no .kicad_pro yet"; fi
  done
fi

fail=0
rows=()
for b in "${boards[@]}"; do
  name="$(basename "$b")"
  pro="$(compgen -G "$b/*.kicad_pro" | head -n1 || true)"
  [[ -n "$pro" ]] || { echo "SKIP $name: no .kicad_pro"; continue; }
  base="${pro%.kicad_pro}"
  sch="$base.kicad_sch"; pcb="$base.kicad_pcb"
  [[ -f "$sch" ]] || { echo "SKIP $name: no schematic"; continue; }

  echo "== $name"
  out="$b/reports"; mkdir -p "$out"
  ok=1

  kicad sch erc --format json --severity-all --exit-code-violations -o "$out/erc.json" "$sch" || ok=0
  kicad sch erc --format report --severity-all -o "$out/erc.rpt" "$sch" || ok=0
  erc_e="$(jq "$ERC_ERR" "$out/erc.json" 2>/dev/null || echo '?')"
  erc_w="$(jq "$ERC_WARN" "$out/erc.json" 2>/dev/null || echo '?')"

  drc_e="-"; drc_w="-"
  if [[ -f "$pcb" ]] && ! grep -q '(layer "Edge.Cuts")' "$pcb"; then
    echo "   DRC skipped: no board outline (Edge.Cuts) yet"   # layout not started
  elif [[ -f "$pcb" ]]; then
    kicad pcb drc --format json --severity-all --schematic-parity --exit-code-violations -o "$out/drc.json" "$pcb" || ok=0
    kicad pcb drc --format report --severity-all --schematic-parity -o "$out/drc.rpt" "$pcb" || ok=0
    drc_e="$(jq "$DRC_ERR" "$out/drc.json" 2>/dev/null || echo '?')"
    drc_w="$(jq "$DRC_WARN" "$out/drc.json" 2>/dev/null || echo '?')"
  fi

  kicad sch export bom -o "$out/bom.csv" "$sch" || ok=0
  kicad sch export netlist -o "$out/netlist.net" "$sch" || ok=0
  kicad sch export pdf -o "$out/$(basename "$base").pdf" "$sch" || ok=0
  echo "   reports: ${out#"$PCB_DIR/"}/"

  [[ $ok -eq 1 ]] || fail=1
  for n in "$erc_e" "$drc_e"; do
    [[ "$n" == "-" || "$n" == "0" ]] || fail=1   # errors, or '?' = unreadable report
  done
  rows+=("$name|$erc_e|$erc_w|$drc_e|$drc_w")
done

echo
if [[ ${#rows[@]} -eq 0 ]]; then
  echo "No boards with a schematic to check."
else
  fmt="%-26s %10s %12s %10s %12s\n"
  # shellcheck disable=SC2059
  printf "$fmt" BOARD "ERC errors" "ERC warnings" "DRC errors" "DRC warnings"
  for r in "${rows[@]}"; do
    IFS='|' read -r n a c d e <<<"$r"
    # shellcheck disable=SC2059
    printf "$fmt" "$n" "$a" "$c" "$d" "$e"
  done
fi

if [[ $fail -ne 0 ]]; then echo; echo "FAIL: error-severity violations (or kicad-cli failure) above."; exit 1; fi
echo; echo "OK"
