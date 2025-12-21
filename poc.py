#!/tmp/tmp.1h2ylqAG13/bin/python

import pathlib

from inotify import adapters, constants

MASK = constants.IN_MOVE | constants.IN_DELETE

def main():
    maildir = pathlib.Path.home() / "Maildir"
    # keep track of in-flight deliveries
    deliveries = []
    i = adapters.Inotify()
    i.add_watch(str(maildir / ".Spam" / "cur"), mask=MASK)
    for event in i.event_gen(yield_nones=False):
        (_, event_type, path, filename) = event
        if "IN_MOVED_FROM" in event_type:
            # marked as read?
            if filename.endswith(","):
                print("Spam marked as read")
                continue
        if "IN_MOVED_TO" in event_type:
            # fresh delivery, therefore no flags
            if filename.endswith(","):
                print(f"Fresh message {filename}")
                deliveries.append(filename)
                continue
            if filename.endswith(",S"):
                # now seen, is it a delivery?
                print(f"Seen message {filename}")
                if filename[:-1] in deliveries:
                    print("In deliveries, removing")
                    deliveries.remove(filename[:-1])
                    continue
                # not a delivery, it's been moved into spam
                print(f"Train {filename} as spam")
                continue
        if "IN_DELETE" in event_type:
            # has it been moved out?
            if maildir.rglob(filename):
                print(f"Train {filename} as ham")
                continue
            # it's just been deleted, ignore
            continue

        # fallback
        print(f"Unhandled EVENT={event_type}, FILENAME={filename}")


if __name__ == '__main__':
    main()
