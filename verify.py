import argparse
import os
import time
import traceback
from dataclasses import dataclass

import yaml
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


def verify(catalogue_path: str, schedule_path: str):
    with open(catalogue_path) as stream:
        catalogue = yaml.safe_load(stream)

    with open(schedule_path) as stream:
        schedule = yaml.safe_load(stream)

    taken = set[str]()
    total_credits = 0

    for semester, names in schedule.items():
        credits = 0

        if names is not None:
            for name in names:
                try:
                    course = catalogue[name]
                except:
                    if name is not None:
                        print(f"❌ {semester}: {name} not found in catalogue")
                    continue

                if name in taken:
                    print(f"❌ {semester}: {name} already taken")

                if "requires" in course:
                    for required in course["requires"]:
                        if required not in taken:
                            print(f"❌ {semester}: {name} requires {required}")
                            continue

                credits += course["credits"]

            for name in names:
                taken.add(name)

        if credits < 12:
            print(f"❌ {semester}: {credits} credits is too few")
        elif credits > 21:
            print(f"❌ {semester}: {credits} credits is too many")
        else:
            print(f"✅ {semester}: Valid with {credits} credits")

        total_credits += credits

    if diff := set(catalogue.keys()).difference(taken):
        missing_credits = sum(catalogue[n]["credits"] for n in diff)

        print(
            f"❌ Missing {len(diff)} courses worth {missing_credits} credits: ",
            end="",
        )

        if len(diff) > 3:
            print()
            for i, n in enumerate(sorted(diff)):
                print(f"  {i+1}. {n}")
        else:
            print(f"{', '.join(diff)}")
    print(f"\n=============\n\nTaking {total_credits} credits in total")


@dataclass
class Config:
    catalogue: str
    schedule: str


config: Config | None = None


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event: FileSystemEvent):
        os.system("clear")
        try:
            assert config is not None
            verify(
                catalogue_path=config.catalogue, schedule_path=config.schedule
            )
        except:
            print(f"❌ Error Occurred:")
            print(traceback.format_exc())


def main():
    global config
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--catalogue",
        type=str,
        default="catalogue.yaml",
        help="Catalogue file",
    )
    parser.add_argument(
        "-s",
        "--schedule",
        type=str,
        default="schedule.yaml",
        help="Schedule file",
    )
    args = parser.parse_args()
    config = Config(**vars(args))

    event_handler = MyHandler()
    observer = Observer()

    observer.schedule(event_handler, config.schedule, recursive=True)  # type: ignore
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
