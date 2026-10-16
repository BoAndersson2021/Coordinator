#!/usr/bin/env python3
"""Fail-closed local bootstrap planner for AgenticGameStudioInstallation v0.2.

No shell commands, network requests, dependency installation, or external mutations.
Only approved staging of exact source documents and manifest is implemented.
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

REQUIRED_BINDINGS = ('studio_root','project_root','corpus_authoritative_store','corpus_retrieval_index','source_repository','repository_integration_adapter','task_state_store','execution_receipt_store','artifact_store','execution_sandbox_provider','build_executor','test_executor','runtime_target','release_staging_store','promotion_authority_service','publication_adapter','secrets_provider','agent_model_provider','agent_dispatch_adapter')
ALLOWED_PHASES = ['discover','inspect','resolve_sources','validate_contracts','generate_plan','approve_plan','provision_staging','verify_staging','authorize_promotion','promote_installation','qualify']


def digest(data): return hashlib.sha256(data).hexdigest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def save_json(path, data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink(): raise ValueError('Refusing symlink output')
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.pending-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(data,f,indent=2,sort_keys=True,ensure_ascii=False)
            f.write('\n'); f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def load(manifest):
    raw=Path(manifest).read_bytes()
    m=yaml.safe_load(raw)
    if not isinstance(m,dict) or m.get('kind')!='AgenticGameStudioInstallation' or str(m.get('schema_version'))!='0.2': raise ValueError('Unsupported manifest schema or kind')
    install=m.get('installation',{})
    if install.get('mode')!='plan_then_approve_then_apply_then_qualify' or install.get('default_action')!='inspect_only' or install.get('failure_policy')!='fail_closed': raise ValueError('Unsafe installation policy')
    if install.get('phases')!=ALLOWED_PHASES: raise ValueError('Unexpected installation phases')
    if any(install.get(k)!='prohibit' for k in ('privilege_escalation','provider_fallback','implicit_network_access','automatic_purchase','overwrite_existing_authority')): raise ValueError('Missing prohibitions')
    return m,digest(raw)

def safe_source(root,filename):
    if not isinstance(filename,str) or not filename or '\\' in filename:
        raise ValueError('Invalid source path')
    rel=Path(filename)
    if rel.is_absolute() or any(x in ('.','..') for x in rel.parts):
        raise ValueError('Source must be a relative path within source directory')
    p=root
    for part in rel.parts:
        p=p/part
        if p.is_symlink(): raise ValueError('Symlink source forbidden: '+filename)
    if not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Missing or unsafe source: '+filename)
    return p

def discover():
    return {'os':platform.system(),'release':platform.release(),'machine':platform.machine(),'python':platform.python_version(),'tools':{x:shutil.which(x) for x in ('git','cmake','ninja','UnrealEditor','blender')},'yaml_parser':yaml.__version__}

def build_plan(manifest,source_dir):
    m,md=load(manifest)
    root=Path(source_dir).resolve(strict=True)
    sources=[]; blockers=[]
    for s in m.get('sources',{}).get('required',[]):
        try:
            p=safe_source(root,s['file']); actual=digest(p.read_bytes()); expected=s.get('sha256');
            if not expected or actual!=expected: raise ValueError('Source digest mismatch: '+s['file']);
            sources.append({'id':s['id'],'filename':s['file'],'sha256':actual,'size':p.stat().st_size})
        except (KeyError,ValueError,OSError) as e: blockers.append(str(e))
    if not sources: blockers.append('No validated source documents')
    if len(sources)!=len(m.get('sources',{}).get('required',[])): blockers.append('Required source set incomplete')
    bindings=m.get('bindings',{})
    missing=[k for k in REQUIRED_BINDINGS if not bindings.get(k)]
    if missing: blockers.append('Unresolved bindings: '+', '.join(missing))
    unresolved=m.get('unresolved_installation_dependencies',[])
    if unresolved: blockers.append('Unresolved implementation dependencies: '+', '.join(unresolved))
    if m.get('project_contract',{}).get('identity',{}).get('project_id') is None: blockers.append('Missing project identity')
    if m.get('qualification',{}).get('default_status')!='unverified': raise ValueError('Unsafe qualification default')
    plan={'plan_schema':1,'manifest_sha256':md,'manifest_name':Path(manifest).name,'sources':sources,'environment':discover(),'bindings':bindings,'missing_bindings':missing,'unresolved_dependencies':unresolved,'blockers':blockers,'actions':[{'type':'stage_exact_sources','scope':'new_empty_directory_only','files':[x['filename'] for x in sources]+[Path(manifest).name]}],'promotion_allowed':False,'qualification':'unverified'}
    plan['plan_sha256']=digest(canonical(plan))
    return plan

def verify_plan(plan,manifest,source_dir):
    expected=build_plan(manifest,source_dir)
    if canonical(plan)!=canonical(expected): raise ValueError('Plan drift: manifest, sources, environment or bindings changed; replan')
    return expected

def approve(plan_path,manifest,source_dir,approval_path,operator):
    plan=read_json(plan_path);verify_plan(plan,manifest,source_dir)
    if not operator.strip(): raise ValueError('Explicit operator identity required')
    if len(plan['sources'])!=len(load(manifest)[0]['sources']['required']): raise ValueError('Source validation blocked; approval forbidden')
    approval={'schema_version':1,'plan_sha256':plan['plan_sha256'],'operator':operator,'authorization':'stage_exact_sources_only','promotion_authorized':False}
    save_json(approval_path,approval)
    return approval

def stage(plan_path,approval_path,manifest,source_dir,destination):
    plan=read_json(plan_path);verify_plan(plan,manifest,source_dir)
    approval=read_json(approval_path)
    if len(plan['sources'])!=len(load(manifest)[0]['sources']['required']): raise ValueError('Source validation blocked; staging forbidden')
    if approval.get('plan_sha256')!=plan['plan_sha256'] or approval.get('authorization')!='stage_exact_sources_only' or approval.get('promotion_authorized') is not False or not approval.get('operator'): raise ValueError('Approval missing or invalid')
    target=Path(destination).absolute()
    if target.is_symlink() or target.exists(): raise ValueError('Destination must not exist (no overwrite)')
    if not target.parent.is_dir() or target.parent.is_symlink(): raise ValueError('Destination parent must exist and not be a symlink')
    # Source and target must be disjoint. Never stage over source files.
    if target==Path(source_dir).resolve() or Path(source_dir).resolve() in target.parents: raise ValueError('Destination nested inside source directory')
    tmp=Path(tempfile.mkdtemp(prefix='.ags-staging-',dir=target.parent))
    try:
        for src in plan['sources']:
            p=safe_source(Path(source_dir).resolve(),src['filename']);data=p.read_bytes()
            if digest(data)!=src['sha256']: raise ValueError('Source changed during staging')
            out=tmp/src['filename'];out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        raw=Path(manifest).read_bytes()
        if digest(raw)!=plan['manifest_sha256']: raise ValueError('Manifest changed during staging')
        (tmp/plan['manifest_name']).write_bytes(raw)
        evidence={'plan_sha256':plan['plan_sha256'],'status':'staged_unqualified','operator':approval['operator'],'files':{str(p.relative_to(tmp)):digest(p.read_bytes()) for p in tmp.rglob('*') if p.is_file()}}
        (tmp/'staging-receipt.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
        os.rename(tmp,target)
        return evidence
    finally:
        if tmp.exists(): shutil.rmtree(tmp)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['discover','plan','approve','stage','qualify'])
    p.add_argument('--manifest',default='agentic-studio.install.yaml')
    p.add_argument('--source-dir',default='.')
    p.add_argument('--plan',default='studio-plan.json')
    p.add_argument('--approval',default='studio-approval.json')
    p.add_argument('--operator')
    p.add_argument('--destination')
    a=p.parse_args()
    try:
        if a.command=='discover': result=discover()
        elif a.command=='plan':
            result=build_plan(a.manifest,a.source_dir);save_json(a.plan,result)
        elif a.command=='approve':
            if not a.operator: raise ValueError('--operator required')
            result=approve(a.plan,a.manifest,a.source_dir,a.approval,a.operator)
        elif a.command=='stage':
            if not a.destination: raise ValueError('--destination required')
            result=stage(a.plan,a.approval,a.manifest,a.source_dir,a.destination)
        else:
            plan=read_json(a.plan);verify_plan(plan,a.manifest,a.source_dir)
            result={'qualification':'blocked','reason':'No executable component adapters, authority enforcement or qualification tests are bound','blockers':plan['blockers'],'gates':{x['id']:'unverified' for x in load(a.manifest)[0]['qualification']['gates']}}
        print(json.dumps(result,indent=2,sort_keys=True))
        if a.command=='qualify' or (a.command=='plan' and result['blockers']): return 2
        return 0
    except (OSError,ValueError,KeyError,yaml.YAMLError) as e:
        print('ERROR: '+str(e),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
