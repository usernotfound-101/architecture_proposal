#!/usr/bin/env bash
set -euo pipefail

# Provision ADN topology in Tenant_Common:
# mn-cse-tenant-a
#   - AE-node1, AE-node2, AE-node3
#   - node-node1, node-node2, node-node3
#   - mgo-node1 under node-node1, etc.
#   - grp-water (node1,node2), grp-soil (node3)
#
# This script is idempotent enough for repeated runs (400/409 on create are tolerated).

HOST="${HOST:-localhost}"
PORT="${PORT:-7601}"
CSEBASE_RN="${CSEBASE_RN:-mn-cse-tenant-a}"
ADMIN_ORIGIN="${ADMIN_ORIGIN:-SM}"
M2M_USER="${M2M_USER:-}"
EXTRA_CURL_ARGS="${EXTRA_CURL_ARGS:-}"

BASE_URL="http://${HOST}:${PORT}/${CSEBASE_RN}"

log() {
  echo "[$(date +%H:%M:%S)] $*"
}

call_m2m() {
  local method="$1"
  local url="$2"
  local origin="$3"
  local ctype="${4:-}"
  local body="${5:-}"

  local req_id="setup-$(date +%s%N)"
  local body_file
  body_file="$(mktemp)"

  local -a curl_cmd=(curl -sS -o "$body_file" -w '%{http_code}' -X "$method" "$url"
    -H "X-M2M-Origin: ${origin}"
    -H "X-M2M-RI: ${req_id}"
    -H "X-M2M-RVI: 4")

  if [[ -n "$M2M_USER" ]]; then
    curl_cmd+=(-H "X-M2M-User: ${M2M_USER}")
  fi

  if [[ -n "$ctype" ]]; then
    curl_cmd+=(-H "Content-Type: ${ctype}" -d "$body")
  fi

  if [[ -n "$EXTRA_CURL_ARGS" ]]; then
    # Intended for auth gateways in front of MN (for example: '-H "Authorization: Bearer ..."').
    # shellcheck disable=SC2206
    local extra=( $EXTRA_CURL_ARGS )
    curl_cmd+=("${extra[@]}")
  fi

  local code
  code="$("${curl_cmd[@]}")"

  local resp
  resp="$(cat "$body_file")"
  rm -f "$body_file"

  log "$method $url -> HTTP $code"
  log "Response: ${resp}"

  printf '%s\n' "$code"
}

allow_exists_or_success() {
  local code="$1"
  [[ "$code" == "200" || "$code" == "201" || "$code" == "400" || "$code" == "409" ]]
}

create_ae() {
  local idx="$1"
  local domain="$2"
  local ae_rn="AE-node${idx}"
  local node_rn="node-node${idx}"
  local ae_origin="C-${ae_rn}"

  local payload
  payload='{"m2m:ae":{"rn":"'"$ae_rn"'","api":"Nadn.'"$domain"'.v1","rr":true,"lbl":["domain:'"$domain"'","type:adn","node:'"$node_rn"'"],"poa":["http://localhost:18'"$idx"'0"]}}'

  local code
  code="$(call_m2m "POST" "$BASE_URL" "$ae_origin" "application/json;ty=2" "$payload")"
  allow_exists_or_success "$code" || {
    log "Failed to create ${ae_rn}"
    exit 1
  }
}

create_node() {
  local idx="$1"
  local domain="$2"
  local node_rn="node-node${idx}"

  local payload
  payload='{"m2m:nod":{"rn":"'"$node_rn"'","ni":"ni-'"$node_rn"'","hcl":1,"mgca":["battery","connectivity"],"lbl":["domain:'"$domain"'","type:node"]}}'

  local code
  code="$(call_m2m "POST" "$BASE_URL" "$ADMIN_ORIGIN" "application/json;ty=14" "$payload")"
  allow_exists_or_success "$code" || {
    log "Failed to create ${node_rn}"
    exit 1
  }
}

create_mgo() {
  local idx="$1"
  local domain="$2"
  local node_rn="node-node${idx}"
  local mgo_rn="mgo-node${idx}"

  local payload
  payload='{"m2m:mgo":{"rn":"'"$mgo_rn"'","mgd":1001,"obis":"device-status","obps":{"domain":"'"$domain"'","node":"'"$node_rn"'"},"dc":"generic mgmt object"}}'

  local code
  code="$(call_m2m "POST" "$BASE_URL/$node_rn" "$ADMIN_ORIGIN" "application/json;ty=13" "$payload")"
  allow_exists_or_success "$code" || {
    log "Failed to create ${mgo_rn} under ${node_rn}"
    exit 1
  }
}

create_group() {
  local grp_rn="$1"
  local domain="$2"
  local members_csv="$3"

  IFS=',' read -r -a members <<< "$members_csv"

  local mid_json=""
  local i
  for i in "${!members[@]}"; do
    local rn="${members[$i]}"
    local sid="${CSEBASE_RN}/${rn}"
    if [[ "$i" -gt 0 ]]; then
      mid_json+=","
    fi
    mid_json+="\"${sid}\""
  done

  local payload
  payload='{"m2m:grp":{"rn":"'"$grp_rn"'","mnm":100,"mid":['"$mid_json"'],"lbl":["domain:'"$domain"'","type:group"]}}'

  local code
  code="$(call_m2m "POST" "$BASE_URL" "$ADMIN_ORIGIN" "application/json;ty=9" "$payload")"
  allow_exists_or_success "$code" || {
    log "Failed to create group ${grp_rn}"
    exit 1
  }
}

log "Target CSE base: ${BASE_URL}"

code="$(call_m2m "GET" "$BASE_URL" "$ADMIN_ORIGIN")"
[[ "$code" == "200" ]] || {
  log "CSE base is not reachable"
  exit 1
}

# Node taxonomy example requested by user:
# node1 -> water, node2 -> water, node3 -> soil
create_ae 1 water
create_ae 2 water
create_ae 3 soil

create_node 1 water
create_node 2 water
create_node 3 soil

create_mgo 1 water
create_mgo 2 water
create_mgo 3 soil

create_group "grp-water" "water" "node-node1,node-node2"
create_group "grp-soil" "soil" "node-node3"

log "Provisioning done. Quick discovery checks:"
call_m2m "GET" "$BASE_URL?fu=1&ty=2" "$ADMIN_ORIGIN" >/dev/null
call_m2m "GET" "$BASE_URL?fu=1&ty=14" "$ADMIN_ORIGIN" >/dev/null
call_m2m "GET" "$BASE_URL?fu=1&ty=13" "$ADMIN_ORIGIN" >/dev/null
call_m2m "GET" "$BASE_URL?fu=1&ty=9" "$ADMIN_ORIGIN" >/dev/null

log "Topology now includes AE/node/mgo/group resources for water and soil domains."
