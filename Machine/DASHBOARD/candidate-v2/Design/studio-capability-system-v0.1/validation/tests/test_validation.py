import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validate import validate,load
class TestPackage(unittest.TestCase):
 def test_static_acceptance(self): self.assertEqual(validate()['status'],'static_pass')
 def test_citizen_count(self): self.assertEqual(len(load('registry/citizens.yaml')['citizens']),16)
 def test_inert_tools(self): self.assertTrue(all(not x['enabled'] for x in load('registry/tools.yaml')['entries']))
 def test_no_automatic_activation(self): self.assertFalse(load('handoff/integration.yaml')['installation']['automatic_activation'])
 def test_all_uncertain_effects_block(self):
  from validate import ROOT
  for p in (ROOT/'workflows').glob('*.yaml'):
   self.assertTrue(all(s['on_uncertain_external_effect']=='recovery_required' for s in load(str(p.relative_to(ROOT)))['stages']))
if __name__=='__main__':unittest.main()
