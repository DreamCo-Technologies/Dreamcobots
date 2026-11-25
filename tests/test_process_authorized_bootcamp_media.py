import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import process_authorized_bootcamp_media as media

class AuthorizedMediaTests(unittest.TestCase):
    def test_path_outside_authorized_media_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"clip.mp4"
            path.write_bytes(b"not media")
            with self.assertRaisesRegex(ValueError,"inside data/authorized-media"):
                media.verify_asset(path,"clip",{"assets":[]})
    def test_missing_asset_registration_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); path=root/"clip.mp4"; path.write_bytes(b"sample")
            with patch.object(media,"MEDIA_ROOT",root):
                with self.assertRaisesRegex(ValueError,"not registered"):
                    media.verify_asset(path,"clip",{"assets":[]})
    def test_hash_and_separate_rights_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); path=root/"clip.mp4"; path.write_bytes(b"sample")
            digest=hashlib.sha256(b"sample").hexdigest()
            grant={"asset_id":"clip","sha256":digest,"study_permission":True,
                   "summary_derivative_permission":True,"evaluation_permission":True,
                   "training_permission":False,"evidence_ref":"consent-17"}
            with patch.object(media,"MEDIA_ROOT",root):
                _,found=media.verify_asset(path,"clip",{"assets":[grant]})
                self.assertFalse(found["training_permission"])
                grant["evaluation_permission"]=False
                with self.assertRaisesRegex(ValueError,"evaluation_permission"):
                    media.verify_asset(path,"clip",{"assets":[grant]})
    def test_hash_mismatch_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); path=root/"clip.mp4"; path.write_bytes(b"sample")
            grant={"asset_id":"clip","sha256":"0"*64,"study_permission":True,
                   "summary_derivative_permission":True,"evaluation_permission":True,"evidence_ref":"review"}
            with patch.object(media,"MEDIA_ROOT",root):
                with self.assertRaisesRegex(ValueError,"hash does not match"):
                    media.verify_asset(path,"clip",{"assets":[grant]})

if __name__=="__main__": unittest.main()
