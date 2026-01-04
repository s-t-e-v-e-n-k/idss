import collections
import dataclasses
import logging
import pathlib

from inotify import adapters, constants


class Deliveries:
    def __init__(self):
        self._deliveries = []

    def new(self, filename):
        logging.debug(f"{filename} is a fresh delivery")
        name = MaildirFile(filename).basename
        if name in self._deliveries:
            raise ValueError(f"{filename} already seen")
        self._deliveries.append(name)

    def marked_as_read(self, filename):
        logging.debug(f"{filename} marked as read")
        name = MaildirFile(filename).basename
        if name not in self._deliveries:
            raise ValueError(f"{filename} not seen before")
        self._deliveries.remove(name)

    def __contains__(self, filename):
        return MaildirFile(filename).basename in self._deliveries


# This is what is yielded directly from inotify
# a 4-tuple of header, event_types, path, filename
Event = collections.namedtuple(
    "Event", ["header", "event_types", "path", "filename"]
)


@dataclasses.dataclass
class MaildirFile:
    filename: str

    @property
    def split_by_flags(self):
        return self.filename.rsplit(",", maxsplit=1)

    @property
    def basename(self):
        return self.split_by_flags[0]

    @property
    def flags(self):
        return self.split_by_flags[1]

    @property
    def seen(self):
        return "S" in self.flags


class IDSS:
    def __init__(self):
        self.event_map = self.generate_event_map()
        self.maildir = pathlib.Path.home() / "Maildir"
        self.deliveries = Deliveries()

    def generate_event_map(self):
        event_map = {}
        for kind in ("IN_MOVED_FROM", "IN_MOVED_TO", "IN_DELETE"):
            event_map[kind] = f"{kind.lower()[3:]}_event"
        return event_map

    def train(self, filename, kind="spam"):
        logging.debug(f"Train {filename} as {kind}")

    def process_events(self):
        i = adapters.Inotify()
        mask = constants.IN_MOVE | constants.IN_DELETE
        i.add_watch(str(self.maildir / ".Spam" / "cur"), mask=mask)
        for event_tuple in i.event_gen(yield_nones=False):
            event = Event(*event_tuple)
            event_type = event.event_types[0]
            maildirfile = MaildirFile(event.filename)
            logging.debug(
                f"Calling {self.event_map[event_type]} for {event.filename}"
            )
            if event_type not in self.event_map:
                logging.debug(
                    f"Unknown EVENT={event_type}, FILENAME={event.filename}"
                )
                continue
            getattr(self, self.event_map[event_type])(maildirfile)
            # unhandled events? If they return False??

    def moved_from_event(self, filename: str):
        if not filename.seen:
            logging.warn(f"{filename} not marked as a fresh delivery")

    def moved_to_event(self, filename: str):
        if filename.seen:
            if filename in self.deliveries:
                self.deliveries.marked_as_read(filename)
            else:
                self.train(filename)
        else:
            self.deliveries.new(filename)

    def delete_event(self, filename: str):
        # has it been moved out?
        if self.maildir.rglob(filename):
            self.train(filename, "ham")
