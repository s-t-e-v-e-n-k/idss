import pathlib
import unittest

from idss.idss import File


class TestFile(unittest.TestCase):
    def setUp(self):
        strpath = "1766984234.M162135P1905529.mangled,S=40124,W=41134:2,S"
        path = pathlib.Path(f"/tmp/{strpath}")
        self.file = File(path)

    def test_flags(self):
        pass

    def test_basename(self):
        pass
