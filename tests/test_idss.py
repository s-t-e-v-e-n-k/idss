import pathlib
import unittest
from unittest.mock import Mock, patch

from idss.idss import IDSS, Deliveries, File


class TestFile(unittest.TestCase):
    def setUp(self):
        strpath = "1766984234.M162135P1905529.mangled,S=40124,W=41134:2,S"
        path = pathlib.Path(f"/tmp/{strpath}")
        self.file = File(path)

    def test_split_by_flags(self):
        expected = [
            "1766984234.M162135P1905529.mangled,S=40124,W=41134:2",
            "S",
        ]
        result = self.file.split_by_flags
        self.assertEqual(expected, result)

    def test_basename(self):
        basename = "1766984234.M162135P1905529.mangled,S=40124,W=41134:2"
        self.assertEqual(self.file.basename, basename)

    def test_flags(self):
        self.assertEqual(self.file.flags, "S")

    def test_seen(self):
        self.assertTrue(self.file.seen)


class TestDeliveries(unittest.TestCase):
    def setUp(self):
        self.deliveries = Deliveries()


class TestIDSS(unittest.TestCase):
    def setUp(self):
        self.idss = IDSS()

    def test_event_map(self):
        event_map = {
            "IN_DELETE": "delete_event",
            "IN_MOVED_FROM": "moved_from_event",
            "IN_MOVED_TO": "moved_to_event",
        }
        self.assertEqual(self.idss.event_map, event_map)

    def test_delete_event_calls_train(self):
        with patch.object(IDSS, "train") as train_mock:
            with patch.object(self.idss, "maildir") as maildir_mock:
                maildir_mock.rglob = Mock(return_value=True)
                self.idss.delete_event("foobar")
            train_mock.assert_called_once_with("foobar", "ham")
