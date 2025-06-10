from __future__ import annotations  # noqa: D100

import argparse
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
MULTILINE_PRINT_THRESHOLD = 3


def verify(
    catalog_path: str,
    schedule_path: str,
    min_credits: int,
    max_credits: int,
) -> None:
    """Verify schedule."""
    if not Path(catalog_path).exists():
        msg = "Catalog path does not exist"
        raise ValueError(msg)
    if not Path(schedule_path).exists():
        msg = "Schedule path does not exist"
        raise ValueError(msg)

    with Path(catalog_path).open() as stream:
        catalog = yaml.safe_load(stream)
    if catalog is None:
        sys.exit("failed to load catalog")

    with Path(schedule_path).open() as stream:
        schedule = yaml.safe_load(stream)
    if schedule is None:
        sys.exit("failed to load schedule")

    taken = set[str]()
    total_credits = 0
    for semester, names in schedule.items():
        total_credits += verify_semester(
            catalog,
            taken,
            semester,
            names,
            min_credits,
            max_credits,
        )

    if diff := set(catalog.keys()).difference(taken):
        missing_credits = sum(catalog[n]["credits"] for n in diff)
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
            logger.info(", ".join(map(str, diff)))
    logger.info("\n=============\n\nTaking %s credits in total", total_credits)


def verify_semester(
    catalog: dict[str, dict[str, str | int | list[str]]],
    taken: set[str],
    semester: str,
    names: list[str],
    min_credits: int,
    max_credits: int,
) -> int:
    """Verify semester and return credits."""
    course_credits = 0

    if names is not None:
        for name in names:
            if name not in catalog:
                logger.warning(
                    "❌ %s: %s not found in catalog",
                    semester,
                    name,
                )
                continue

            course = catalog[name]

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

            if not isinstance(course["credits"], int):
                msg = "course 'credits' must be int"
                raise TypeError(msg)
            course_credits += course["credits"]
            taken.add(name)

    validate_credits(semester, course_credits, min_credits, max_credits)

    return course_credits


def validate_credits(
    semester: str,
    course_credits: int,
    min_credits: int,
    max_credits: int,
) -> None:
    """Validate the course credits."""
    if course_credits < 0:
        msg = "Course credits cannot be below 0"
        raise ValueError(msg)

    if course_credits < min_credits:
        logger.warning(
            "❌ %s: %s credits is too few",
            semester,
            course_credits,
        )
    elif course_credits > max_credits:
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

    catalog: str
    schedule: str
    min_credits: int
    max_credits: int


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
                catalog_path=self.config.catalog,
                schedule_path=self.config.schedule,
                min_credits=self.config.min_credits,
                max_credits=self.config.max_credits,
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
        "--catalog",
        type=str,
        default="./examples/catalogs/catalog.yaml",
        help="catalog file",
    )
    parser.add_argument(
        "-s",
        "--schedule",
        type=str,
        default="./examples/schedules/full_schedule-2.yaml",
        help="Schedule file",
    )
    parser.add_argument(
        "--min-credits",
        type=int,
        default=12,
        help="min credits per semester",
    )
    parser.add_argument(
        "--max-credits",
        type=int,
        default=21,
        help="max credits per semester",
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
