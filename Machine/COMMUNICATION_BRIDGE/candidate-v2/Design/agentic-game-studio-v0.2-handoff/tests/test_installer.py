import importlib.util, tempfile, pathlib, shutil, unittest, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'installer'/'installer.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class InstallerTests(unittest.TestCase):
    def test_plan_and_staging(self):
        with tempfile.TemporaryDirectory() as d:
            base=pathlib.Path(d);p=mod.build_plan(ROOT/'agentic-studio.install.yaml',ROOT)
            self.assertTrue(p['blockers']);self.assertFalse(p['promotion_allowed'])
            mod.save_json(base/'plan.json',p)
            mod.approve(base/'plan.json',ROOT/'agentic-studio.install.yaml',ROOT,base/'approval.json','operator')
            receipt=mod.stage(base/'plan.json',base/'approval.json',ROOT/'agentic-studio.install.yaml',ROOT,base/'staging')
            self.assertEqual(receipt['status'],'staged_unqualified')
            self.assertTrue((base/'staging'/'corpus'/'architecture-v1.2.txt').exists())
            with self.assertRaises(ValueError): mod.stage(base/'plan.json',base/'approval.json',ROOT/'agentic-studio.install.yaml',ROOT,base/'staging')
    def test_bad_digest_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            base=pathlib.Path(d);shutil.copytree(ROOT/'corpus',base/'corpus');shutil.copy2(ROOT/'agentic-studio.install.yaml',base/'agentic-studio.install.yaml')
            (base/'corpus'/'architecture-v1.2.txt').write_text('changed')
            p=mod.build_plan(base/'agentic-studio.install.yaml',base)
            self.assertTrue(any('digest mismatch' in x for x in p['blockers']))
            mod.save_json(base/'plan.json',p)
            with self.assertRaises(ValueError):mod.approve(base/'plan.json',base/'agentic-studio.install.yaml',base,base/'approval.json','operator')
    def test_path_escape_denied(self):
        with self.assertRaises(ValueError):mod.safe_source(ROOT,'../etc/passwd')
if __name__=='__main__':unittest.main()
