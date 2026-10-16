#!/usr/bin/env python3
"""Offline static validator; no external effects."""
from pathlib import Path
import hashlib, json, sys
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(rel):
 p=ROOT/rel
 if p.is_symlink() or not p.is_file(): raise ValueError('missing/unsafe: '+rel)
 v=yaml.safe_load(p.read_text(encoding='utf-8'))
 if not isinstance(v,dict) or v.get('schema_version')!=1: raise ValueError('schema: '+rel)
 return v
def validate():
 c=load('registry/citizens.yaml')['citizens']
 ids=[x['id'] for x in c]
 if len(ids)!=16 or len(set(ids))!=16 or ids!=['CIT-%02d'%i for i in range(1,17)]: raise ValueError('citizen identity/count')
 for x in c:
  for field in ('key','name','category','authority_owner','responsibility','inputs','outputs','dependencies','permitted_effects','prohibited_effects','state_owner','mutation_boundary','failure_mode','verification'):
   if field not in x or x[field] in (None,'',[]):
    if field not in ('dependencies',): raise ValueError('missing citizen field '+x['id']+':'+field)
  if not set(x['dependencies']).issubset(set(ids)): raise ValueError('unknown dependency')
  if not set(('self_approve_protected_mutation','invent_missing_authority','promote_unverified_candidate')).issubset(set(x['prohibited_effects'])): raise ValueError('missing prohibitions')
  if x['mutation_boundary'] not in ('candidate_only_unless_separately_authorized','authority_service_only','domain_owners_commit_only'): raise ValueError('unsafe mutation boundary')
 for r in ('laws','rules','contracts','tools'):
  items=load('registry/'+r+'.yaml')['entries']
  keys=[x['id'] for x in items]
  if not keys or len(set(keys))!=len(keys): raise ValueError('duplicate/empty '+r)
  if r=='tools' and any(x['enabled'] or x['implementation']!='unbound' for x in items): raise ValueError('unqualified tool enabled')
 contracts=load('registry/contracts.yaml')['entries']
 for x in contracts:
  y=load('contracts/'+x['id'][4:].lower().replace('-','_')+'.contract.yaml')
  if y['contract_id']!=x['id'] or y['implementation_status']!='declarative_unenforced' or not y['grant_required_for_mutation']: raise ValueError('contract inconsistency')
 for p in sorted((ROOT/'workflows').glob('*.yaml')):
  w=load(str(p.relative_to(ROOT)))
  if not w['stages'] or w['approval']!='required_at_protected_mutation' or w['max_unbounded_retries']!=0: raise ValueError('unsafe workflow')
  if any(s['on_uncertain_external_effect']!='recovery_required' for s in w['stages']): raise ValueError('unsafe uncertainty')
 h=load('handoff/integration.yaml')
 if h['compatibility']!={'studio_handoff':'0.2','project_architecture':'1.2'} or h['installation']['automatic_activation'] or h['authority']['may_override_baseline']: raise ValueError('unsafe compatibility')
 inventory=json.loads((ROOT/'handoff/inventory.json').read_text())
 actual={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).as_posix() not in ('handoff/inventory.json',) and '__pycache__' not in p.parts and p.suffix!='.pyc'}
 if inventory['files']!=actual: raise ValueError('inventory mismatch')
 return {'status':'static_pass','citizens':len(c),'contracts':len(contracts),'workflows':len(list((ROOT/'workflows').glob('*.yaml'))),'files':len(actual),'operational_qualification':'unverified'}
if __name__=='__main__':
 try: print(json.dumps(validate(),indent=2))
 except Exception as e: print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
