#!/usr/bin/env python3
"""Synthetic-only portable kit, tampering, detached runtime, and privacy tests."""
from __future__ import annotations
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from build_stage3d_ae_ah_review_desk import build
from test_stage3d_ae_ah_review_desk import fixture
from build_stage3d_am_ap_portable_reviewer_kit import ROOT,bundle,write_archive
from stage3d_ao_verify_portable_kit import verify
from stage3d_an_offline_batch_audit import batch_audit


class PortableKitTests(unittest.TestCase):
    def setUp(self):
        self.desk=build(fixture())
        self.tools_root=Path(__file__).resolve().parent

    def test_complete_source_only_kit_and_manifest(self):
        entries=bundle(self.desk,self.tools_root)
        self.assertEqual(len(entries),18)
        self.assertIn("FILE_MANIFEST.json",entries)
        self.assertEqual(sum(k.endswith("_BLANK.json") for k in entries),5)
        self.assertEqual(sum(k.endswith("_NOT_SENT.md") for k in entries),5)
        self.assertNotIn("PRIVATE_EVIDENCE",json.dumps(sorted(entries)))
        self.assertIn(b"NOT SENT",entries["requests/REQUEST_WA26-003_NOT_SENT.md"])

    def test_real_merged_tools_run_standalone_outside_git_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            archive=root/"review.zip"
            x=write_archive(self.desk,self.tools_root,archive)
            self.assertEqual(x["confirmed_dams"],0)
            with ZipFile(archive) as z:z.extractall(root)
            kit=root/ROOT.rstrip("/")
            self.assertTrue(verify(kit)["all_digests_match"])
            private=root/"private_evidence"
            private.mkdir()
            script=kit/"tools/stage3d_ai_ak_private_evidence_intake.py"
            desk=kit/"SOURCE_DESK_UNVERIFIED.json"
            case=private/"WA26-003.json"
            proc=subprocess.run([sys.executable,str(script),"--desk",str(desk),
               "--case","WA26-003","--init","--out",str(case)],
               cwd=str(root),capture_output=True,text=True,timeout=8)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertFalse(json.loads(case.read_text())["documents"])
            batch=kit/"tools/stage3d_an_offline_batch_audit.py"
            status=private/"batch-status.json"
            proc=subprocess.run([sys.executable,str(batch),"--desk",str(desk),
               "--private-dir",str(private),"--out",str(status)],
               cwd=str(root),capture_output=True,text=True,timeout=8)
            self.assertEqual(proc.returncode,0,proc.stderr)
            report=json.loads(status.read_text())
            self.assertEqual(report["not_submitted_count"],4)
            self.assertEqual(report["independently_confirmed_dams"],0)
            self.assertFalse(report["public_map_updated"])
            self.assertNotIn("reviewer_name",json.dumps(report))
            self.assertNotIn("evidence_locator",json.dumps(report))

    def test_checksum_integrity_detects_modified_source_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            archive=root/"review.zip"
            write_archive(self.desk,self.tools_root,archive)
            with ZipFile(archive) as z:z.extractall(root)
            kit=root/ROOT.rstrip("/")
            self.assertTrue(verify(kit)["all_digests_match"])
            readme=kit/"README_FIRST.md"
            readme.write_text(readme.read_text()+"\nCORRUPTED\n")
            with self.assertRaises(ValueError):verify(kit)

    def test_rejects_changed_approved_dam_source(self):
        x=copy.deepcopy(self.desk);x["independently_confirmed_dams"]=1
        with self.assertRaises(ValueError):bundle(x,self.tools_root)

    def test_missing_case_is_not_assessed_or_approved(self):
        with tempfile.TemporaryDirectory() as directory:
            report=batch_audit(self.desk,Path(directory))
            self.assertEqual(report["not_submitted_count"],5)
            self.assertEqual(report["structurally_complete_second_review_candidates"],0)
            self.assertFalse(report["approval_is_technically_possible_from_this_tool"])
            self.assertEqual(len(report["cases"]),5)

    def test_invalid_private_form_is_not_exposed_in_status(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"WA26-083.json"
            p.write_text('{"person_name":"PRIVATE PERSON","evidence_locator":"/secret/folder"}')
            status=batch_audit(self.desk,Path(directory))
            self.assertEqual(status["invalid_form_count"],1)
            self.assertNotIn("PRIVATE PERSON",json.dumps(status))
            self.assertNotIn("/secret/folder",json.dumps(status))

    def test_private_symlinks_rejected_without_following(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            other=root/"sensitive.txt";other.write_text("SECRET")
            private=root/"private";private.mkdir()
            try:(private/"WA26-083.json").symlink_to(other)
            except (OSError,NotImplementedError):self.skipTest("Symlinks unavailable")
            report=batch_audit(self.desk,private)
            self.assertEqual(report["invalid_form_count"],1)
            self.assertNotIn("SECRET",json.dumps(report))

    def test_output_archive_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"review.zip"
            write_archive(self.desk,self.tools_root,p)
            with self.assertRaises(ValueError):write_archive(self.desk,self.tools_root,p)

    def test_source_desk_changes_rejected_by_batch(self):
        d=copy.deepcopy(self.desk);d["public_map_changes"]=True
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):batch_audit(d,Path(directory))

    def test_zip_paths_safely_scoped(self):
        with tempfile.TemporaryDirectory() as directory:
            f=Path(directory)/"archive.zip"
            write_archive(self.desk,self.tools_root,f)
            with ZipFile(f) as z:
                self.assertIsNone(z.testzip())
                self.assertTrue(all(n.startswith(ROOT) and ".." not in Path(n).parts
                    and not n.startswith("/") for n in z.namelist()))

if __name__=="__main__":unittest.main()
