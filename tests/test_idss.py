import unittest
from unittest.mock import Mock, patch

from idss.idss import IDSS, Deliveries, Event, MaildirFile


class TestEvent(unittest.TestCase):
    def test_event(self):
        event_tuple = ("header", ["IN_CREATE"], "/tmp", "foobar")
        event = Event(*event_tuple)
        self.assertEqual(event.header, "header")
        self.assertEqual(len(event.event_types), 1)
        self.assertEqual(event.event_types[0], "IN_CREATE")
        self.assertEqual(event.path, "/tmp")
        self.assertEqual(event.filename, "foobar")


class TestMaildirFile(unittest.TestCase):
    def setUp(self):
        filename = "1766984234.M162135P1905529.mangled,S=40124,W=41134:2,S"
        self.file = MaildirFile(filename)

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

    def test_in_empty(self):
        self.assertNotIn("foobar", self.deliveries)

    def test_new(self):
        self.deliveries.new("foobar")
        self.assertIn("foobar", self.deliveries)

    def test_double_new(self):
        self.deliveries.new("foobar")
        with self.assertRaises(ValueError):
            self.deliveries.new("foobar")

    def test_marked_as_read_empty(self):
        with self.assertRaises(ValueError):
            self.deliveries.marked_as_read("foobar")

    def test_full(self):
        self.deliveries.new("foobar")
        self.assertIn("foobar", self.deliveries)
        self.deliveries.marked_as_read("foobar")
        self.assertNotIn("foobar", self.deliveries)


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
