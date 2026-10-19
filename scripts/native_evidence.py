"""Strict evidence reader shared by the native control command. No dispatch authority."""
import hashlib
import json
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path

TOP = set("format origin run_id operation_id observed_at_utc scope actors source connection effective_settings evidence_root limits observations collection artifacts unresolved_effects owner_acceptance unknowns".split())
OBJECTS = {
    "scope": set("kind mission operation authority_reference repository_root worktree_root".split()),
    "actors": {"coordinator_session_id", "receiver_session_id"},
    "source": set("head client_sha256 dependencies_sha256 dirty_manifest_sha256".split()),
    "connection": set("endpoint backend_binding backend_generation cli_version server_version cli_sha256 server_sha256".split()),
    "effective_settings": {"approval_policy", "approvals_reviewer", "permission_scope"},
    "collection": {"complete", "gaps"},
    "owner_acceptance": {"decision", "scope", "authority_reference"},
}
BUDGETS = {"connect_seconds": 5, "rpc_seconds": 10, "reconcile_seconds": 30,
           "frame_bytes": 1048576, "queued_events": 32, "evidence_bytes": 5242880,
           "retention_review_days": 7}


def strict_json(value):
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = item
        return result
    def invalid(value):
        raise ValueError("Non-finite JSON number")
    return json.loads(value, object_pairs_hook=pairs, parse_constant=invalid)


def safe_read(root, relative, maximum):
    """Open each component under a trusted directory fd; never follow a symlink."""
    p = Path(relative)
    require(not p.is_absolute() and p.parts and ".." not in p.parts, "Unsafe artifact path")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in p.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        child = os.open(p.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(child, "rb") as file:
            require(stat.S_ISREG(os.fstat(file.fileno()).st_mode), "Not regular file")
            value = file.read(maximum + 1)
            require(len(value) <= maximum, "Artifact exceeds budget")
            return value
    finally:
        os.close(fd)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def keys(value, expected):
    require(isinstance(value, dict) and set(value) == expected, "Object fields differ")


def null_paths(value, prefix=""):
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if item is None:
                yield path
            elif key != "unknowns":
                yield from null_paths(item, path)


def digest(value, length):
    return isinstance(value, str) and len(value) == length and all(c in "0123456789abcdef" for c in value)


def evaluate(record, trusted_root, trusted_scope):
    invalid = {"record_valid": False, "summary": "invalid", "owner_acceptance": None, "native_qualified": False}
    try:
        keys(record, TOP)
        require(record["format"] == "codeexp2-control-evidence/1", "Unknown format")
        require(record["origin"] in {"fixture", "observed"}, "Unknown origin")
        for name in ["run_id", "operation_id", "observed_at_utc", "evidence_root"]:
            require(text(record[name]), "Missing record identity")
        require(datetime.fromisoformat(record["observed_at_utc"]).utcoffset() == timedelta(0), "Timestamp not UTC")
        for name, fields in OBJECTS.items():
            keys(record[name], fields)
        require(record["scope"]["kind"] in {"workspace-maintenance", "mission"}, "Unknown scope")
        for key in ["operation", "repository_root", "worktree_root"]:
            require(text(record["scope"][key]), "Missing scope")
        for key in ["repository_root", "worktree_root"]:
            p = Path(record["scope"][key])
            require(p.is_absolute() and str(p.resolve()) == str(p), "Root not canonical")
        if record["scope"]["kind"] == "mission":
            require(text(record["scope"]["mission"]), "Mission not named")
        for key, expected in trusted_scope.items():
            require(record["scope"].get(key) == expected, "Trusted scope mismatch")
        for name in ["actors", "source", "connection"]:
            for value in record[name].values():
                require(value is None or text(value), "Identity must be string or explained null")
        for name in ["approval_policy", "approvals_reviewer"]:
            value = record["effective_settings"][name]
            require(value is None or text(value), "Invalid effective setting")
        require(record["effective_settings"]["permission_scope"] is None or isinstance(record["effective_settings"]["permission_scope"], dict), "Invalid permission scope")
        for name in ["source", "connection"]:
            for key, value in record[name].items():
                if key.endswith("sha256") and value is not None:
                    require(digest(value, 64), "Invalid digest")
        if record["source"]["head"] is not None:
            require(digest(record["source"]["head"], 40), "Invalid HEAD")
        require(isinstance(record["unknowns"], dict), "Unknowns not object")
        require(set(null_paths(record)) == set(record["unknowns"]), "Missing or obsolete null explanation")
        require(all(text(v) for v in record["unknowns"].values()), "Empty null explanation")
        root_claim = Path(record["evidence_root"])
        if not root_claim.is_absolute():
            require(record["origin"] == "fixture" and str(root_claim) == ".", "Relative root not allowed")
            root_claim = trusted_root / root_claim
        require(root_claim.resolve() == trusted_root.resolve(), "Evidence root not authorized")
        keys(record["limits"], set(BUDGETS))
        require(all(type(record["limits"][k]) is int and 0 < record["limits"][k] <= v for k, v in BUDGETS.items()), "Unsupported budget")
        collection = record["collection"]
        require(type(collection["complete"]) is bool and isinstance(collection["gaps"], list), "Invalid collection")
        require(all(text(v) for v in collection["gaps"]), "Empty gap")
        require(collection["complete"] == (not collection["gaps"]), "Collection/gaps contradict")
        acceptance = record["owner_acceptance"]
        require(acceptance["decision"] in {"not_requested", "accepted", "changes_required", "rejected"}, "Unknown decision")
        if acceptance["decision"] != "not_requested":
            require(text(acceptance["scope"]) and text(acceptance["authority_reference"]), "Decision lacks scope/reference")
        else:
            require(acceptance["scope"] is None and acceptance["authority_reference"] is None, "Unexpected acceptance")
        require(isinstance(record["unresolved_effects"], list), "Effects not array")
        for effect in record["unresolved_effects"]:
            keys(effect, {"operation_id", "effect", "state", "next_action"})
            require(all(text(v) for v in effect.values()), "Effect not actionable")
        require(isinstance(record["artifacts"], list), "Artifacts not array")
        artifacts = {}
        artifact_bytes = 0
        for artifact in record["artifacts"]:
            keys(artifact, {"id", "path", "sha256", "privacy"})
            require(text(artifact["id"]) and artifact["id"] not in artifacts, "Duplicate artifact identity")
            require(text(artifact["path"]) and digest(artifact["sha256"], 64), "Invalid artifact")
            require(artifact["privacy"] in {"private", "publishable-summary", "public-fixture"}, "Unknown privacy")
            p = Path(artifact["path"])
            require(not p.is_absolute() and ".." not in p.parts, "Artifact escapes root")
            p = (trusted_root / p).resolve()
            require(p.is_relative_to(trusted_root.resolve()), "Symlink escapes root")
            valid_bytes = False
            try:
                data = safe_read(trusted_root, artifact["path"], record["limits"]["evidence_bytes"])
                artifact_bytes += len(data)
                valid_bytes = artifact_bytes <= record["limits"]["evidence_bytes"] and hashlib.sha256(data).hexdigest() == artifact["sha256"]
            except (OSError, ValueError):
                pass
            artifacts[artifact["id"]] = valid_bytes
        observations = record["observations"]
        require(isinstance(observations, list) and bool(observations), "No observations")
        results = []
        for observation in observations:
            keys(observation, {"claim", "kind", "result", "artifact_ids", "reason"})
            require(text(observation["claim"]) and text(observation["reason"]), "Empty claim/reason")
            require(observation["kind"] in {"fixture", "inspection", "native", "visual", "owner"}, "Unknown evidence kind")
            require(observation["result"] in {"pass", "fail", "not_run", "not_proven"}, "Unknown result")
            refs = observation["artifact_ids"]
            require(isinstance(refs, list) and all(text(v) and v in artifacts for v in refs), "Missing artifact ID")
            result = observation["result"]
            if result == "pass" and (not refs or not all(artifacts[v] for v in refs)):
                result = "not_proven"
            results.append(result)
        if not collection["complete"] or record["unresolved_effects"]:
            summary = "not_proven"
        elif "fail" in results:
            summary = "fail"
        elif "not_proven" in results:
            summary = "not_proven"
        elif "not_run" in results:
            summary = "not_run"
        else:
            summary = "pass"
        return {"record_valid": True, "summary": summary, "owner_acceptance": acceptance["decision"], "native_qualified": False}
    except (ValueError, TypeError, KeyError, AttributeError):
        return invalid
