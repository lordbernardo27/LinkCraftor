"""Isolated contract tests. No live queue imports, job store operations or issuance."""
from __future__ import annotations
import ast
import base64
import copy
import importlib.util
import json
import os
import sys
import time
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parent
source = (ROOT / "ak6_signed_execution_grants.py")
scope_source = (ROOT / "scope_snapshot.py")
# scope_snapshot.py is a reference copied from user ZIP for pure isolated testing.
if not scope_source.is_file():
    raise SystemExit("Missing isolated scope snapshot")
tree = ast.parse(scope_source.read_text())
constants = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        key = node.targets[0].id
        if key in ("WORKSPACE_ID", "WORKFLOW_ID", "STAGES"):
            constants[key] = ast.literal_eval(node.value)
constants["EXPECTED_SCOPE"] = frozenset(x[1] for x in constants["STAGES"])
mod = types.ModuleType("backend.server.runtime.universal_runtime_worker_scope_contract")
for k,v in constants.items(): setattr(mod,k,v)
with patch.dict(sys.modules, {mod.__name__:mod}):
    spec = importlib.util.spec_from_file_location("ak6_isolated",source)
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)

private = Ed25519PrivateKey.generate()
public = base64.b64encode(private.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)).decode()
now = int(time.time())
stage, job_id, ref, fp = constants["STAGES"][0]
payload = {
    "version":"AK6-ED25519-v1", "job_id":job_id,
    "workspace_id":constants["WORKSPACE_ID"], "workflow_id":constants["WORKFLOW_ID"],
    "stage":stage, "handler_ref":ref, "registration_fingerprint":fp,
    "worker_id":a.WORKER_ID, "not_before":now-5,"expires_at":now+300,
    "nonce":"nonce-test-"+"a"*32, "actions":["claim","execute"],
}
def envelope(body):
    return {"payload":body,"signature":base64.b64encode(private.sign(a._canonical(body))).decode()}
job = SimpleNamespace(
    job_id=job_id, workspace_id=constants["WORKSPACE_ID"],job_type=stage,status="queued",
    metadata={"stage_reference":{"handler_ref":ref,"registration_fingerprint":fp},
              "coordination":{"workflow_id":constants["WORKFLOW_ID"],"workflow_type":"connect_domain"}}
)
def run(job_value, act="claim", grant=None, key=public):
    with patch.dict(os.environ, {a.KEY_ENV:key,a.GRANTS_ENV:json.dumps({job_id:grant if grant is not None else envelope(payload)})}):
        return a.require_signed_ak6_execution_authority(job=job_value, worker_id=a.WORKER_ID, action=act)
checks = 0
def good(fn):
    global checks
    fn(); checks +=1

def denied(fn,label):
    global checks
    try: fn()
    except PermissionError: checks+=1; return
    raise AssertionError("FAIL expected deny: "+label)

good(lambda: run(job)==payload["nonce"] or (_ for _ in ()).throw(AssertionError()))
denied(lambda: run(job,grant=envelope({**payload,"stage":"other"})),"wrong signed stage")
denied(lambda: run(job,grant={**envelope(payload),"signature":base64.b64encode(b"x"*64).decode()}),"tampered signature")
denied(lambda: run(job,key=base64.b64encode(b"z"*32).decode()),"wrong public key")
denied(lambda: run(SimpleNamespace(**{**vars(job),"job_type":"other"})),"job stage")
denied(lambda: run(SimpleNamespace(**{**vars(job),"workspace_id":"other"})),"workspace")
denied(lambda: run(SimpleNamespace(**{**vars(job),"status":"completed"})),"claim terminal")
denied(lambda: run(job,grant=envelope({**payload,"expires_at":now-1,"not_before":now-301})),"expired")
denied(lambda: run(job,grant=envelope({**payload,"not_before":now+100,"expires_at":now+200})),"future")
denied(lambda: run(job,grant=envelope({**payload,"not_before":now-10,"expires_at":now+2000})),"oversized duration")
denied(lambda: run(job,grant=envelope({**payload,"job_id":"fake"})),"grant job")
denied(lambda: run(job,grant=envelope({**payload,"worker_id":"fake"})),"worker")
denied(lambda: run(job,grant=envelope({**payload,"actions":["execute"]})),"wrong actions")
denied(lambda: run(job,grant=envelope({**payload,"registration_fingerprint":"wrong"})),"registration binding")
denied(lambda: run(job,grant=envelope({**payload,"workflow_id":"wrong"})),"workflow binding")
denied(lambda: run(job,act="execute"),"execute without claim")
claimed = {"job_id":job_id,"workspace_id":constants["WORKSPACE_ID"],"job_type":stage,
           "status":"running","metadata":{**copy.deepcopy(job.metadata),"claimed_by_dequeue":True,
           "worker_id":a.WORKER_ID,"lease_id":"lease-test","assigned_worker_id":a.WORKER_ID}}
good(lambda: run(claimed,act="execute")==payload["nonce"] or (_ for _ in ()).throw(AssertionError()))
denied(lambda: run({**claimed,"metadata":{**claimed["metadata"],"worker_id":"other"}},act="execute"),"claim owner")
denied(lambda: run({**claimed,"metadata":{**claimed["metadata"],"lease_id":None}},act="execute"),"missing lease")
denied(lambda: run({**claimed,"status":"completed"},act="execute"),"terminal execution")
with patch.dict(os.environ,{a.KEY_ENV:"",a.GRANTS_ENV:""}):
    denied(lambda: a.require_signed_ak6_execution_authority(job=job,worker_id=a.WORKER_ID,action="claim"),"unprovisioned")
print(f"PASS: {checks}/{checks} isolated signature and policy checks")
print("PRODUCTION TRUST ISSUER: NOT PROVISIONED")
print("LIVE JOBS / QUEUE: NOT ACCESSED")
