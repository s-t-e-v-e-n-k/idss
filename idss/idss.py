import dataclasses
import logging
import pathlib

from inotify import adapters, constants


class Deliveries:
    def __init__(self):
        self.deliveries = []

    @property
    def new(self, filename):
        pass

    @property
    def marked_as_read(self, filename):
        pass


@dataclasses.dataclass
class File:
    filename: pathlib.Path

    @property
    def basename(self):
        return str(self.filename).rsplit(",", maxsplit=1)

    def flags(self):
        pass


class IDSS:
    def __init__(self):
        mask = constants.IN_MOVE | constants.IN_DELETE
        self.event_map = self.generate_event_map()
        self.maildir = pathlib.Path.home() / "Maildir"
        self.deliveries = Deliveries()
        self.i = adapters.Inotify()
        self.i.add_watch(str(self.maildir / ".Spam" / "cur"), mask=mask)

    def generate_event_map(self):
        event_map = {}
        for kind in ("IN_MOVED_FROM", "IN_MOVED_TO", "IN_DELETE"):
            event_map[kind] = f"{kind.lower()[3:]}_event"
        return event_map

    def train(self, filename, kind="spam"):
        logging.debug(f"Train {filename} as {kind}")

    def process_events(self):
        for event in self.i.event_gen(yield_nones=False):
            (_, event_type, _, filename) = event
            logging.debug(
                "Calling {self.event_map[event_type]} for {filename}"
            )
            if event_type not in self.event_type:
                logging.debug(
                    f"Unhandled EVENT={event_type}, FILENAME={filename}"
                )
                continue
            getattr(self, self.event_map[event_type])(filename)

    def delete_event(self, filename):
        # has it been moved out?
        if self.maildir.rglob(filename):
            self.train(filename, "ham")


# def idss():
#    deliveries = Deliveries()
#    i = adapters.Inotify()
#    for event in i.event_gen(yield_nones=False):
#        filename = File(filepath)
#        if "IN_MOVED_FROM" in event_type:
#            if filename.flags is None:
#                deliveries.new(filename)
#                continue
#        if "IN_MOVED_TO" in event_type:
#            # fresh delivery, therefore no flags
#            if filename.endswith(","):
#                logging.debug(f"Fresh message {filename}")
#                deliveries.append(filename)
#                continue
#            if filename.endswith(",S"):
#                # now seen, is it a delivery?
#                logging.debug(f"Seen message {filename}")
#                if filename[:-1] in deliveries:
#                    logging.debug("In deliveries, removing")
#                    deliveries.remove(filename[:-1])
#                    continue
#                train(filename)
#                # not a delivery, it's been moved into spam
#                logging.debug(f"Train {filename} as spam")
#                continue
#
