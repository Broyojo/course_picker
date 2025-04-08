from __future__ import annotations  # noqa: D100

import argparse
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import yaml
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

MIN_CREDITS = 12
MAX_CREDITS = 21

MULTILINE_PRINT_THRESHOLD = 3


def verify(catalogue_path: str, schedule_path: str) -> None:
    """Verify schedule."""
    if not Path(catalogue_path).exists():
        msg = "Catalog path does not exist"
        raise ValueError(msg)
    if not Path(schedule_path).exists():
        msg = "Schedule path does not exist"
        raise ValueError(msg)

    with Path(catalogue_path).open() as stream:
        catalogue = yaml.safe_load(stream)

    with Path(schedule_path).open() as stream:
        schedule = yaml.safe_load(stream)

    taken = set[str]()
    total_credits = 0
    for semester, names in schedule.items():
        total_credits += verify_semester(catalogue, taken, semester, names)

    if diff := set(catalogue.keys()).difference(taken):
        missing_credits = sum(catalogue[n]["credits"] for n in diff)
        if missing_credits < 0:
            msg = "Missing credits cannot be below 0"
            raise ValueError(msg)

        logger.warning(
            "❌ Missing %s courses worth %s credits: ",
            len(diff),
            missing_credits,
        )

        if len(diff) > MULTILINE_PRINT_THRESHOLD:
            for i, n in enumerate(sorted(diff)):
                logger.info("  %s. %s", i + 1, n)
        else:
            logger.info(", ".join(diff))
    logger.info("\n=============\n\nTaking %s credits in total", total_credits)


def verify_semester(
    catalogue: list[dict[str, str | int | list[str]]],
    taken: set[str],
    semester: str,
    names: list[str],
) -> int:
    """Verify semester and return credits."""
    course_credits = 0

    if names is not None:
        for name in names:
            if name not in catalogue:
                logger.warning(
                    "❌ %s: %s not found in catalogue",
                    semester,
                    name,
                )
                continue

            course = catalogue[name]

            if name in taken:
                logger.warning(
                    "❌ %s: %s already taken",
                    semester,
                    name,
                )

            if "requires" in course:
                if not isinstance(course["requires"], list):
                    msg = "course 'requires' must be list"
                    raise TypeError(msg)
                for required in course["requires"]:
                    if required not in taken:
                        logger.warning(
                            "❌ %s: %s requires %s",
                            semester,
                            name,
                            required,
                        )
                        continue

            if not isinstance(course["credits"], int):
                msg = "course 'credits' must be int"
                raise TypeError(msg)
            course_credits += course["credits"]
            taken.add(name)

    validate_credits(semester, course_credits)

    return course_credits


def validate_credits(semester: str, course_credits: int) -> None:
    """Validate the course credits."""
    if course_credits < 0:
        msg = "Course credits cannot be below 0"
        raise ValueError(msg)

    if course_credits < MIN_CREDITS:
        logger.warning(
            "❌ %s: %s credits is too few",
            semester,
            course_credits,
        )
    elif course_credits > MAX_CREDITS:
        logger.warning(
            "❌ %s: %s credits is too many",
            semester,
            course_credits,
        )
    else:
        logger.info(
            "✅ %s: Valid with %s credits",
            semester,
            course_credits,
        )


@dataclass
class Config:
    """Config for the CLI arguments."""

    catalogue: str
    schedule: str


class MyHandler(FileSystemEventHandler):
    """Handler for analyzing on file save."""

    def __init__(self, config: Config) -> None:
        """Init the object."""
        super().__init__()
        self.config = config

    def on_modified(self, event: FileSystemEvent) -> None:
        """Run when file is saved and modified."""
        _ = event
        subprocess.call(["cls" if os.name == "nt" else "clear"])  # noqa: S603
        try:
            verify(
                catalogue_path=self.config.catalogue,
                schedule_path=self.config.schedule,
            )
        except Exception:
            logger.exception("❌ Error Occurred:")


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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

    event_handler = MyHandler(config)
    observer = Observer()

    observer.schedule(event_handler, config.schedule, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
