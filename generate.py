import copy
import json
from collections import defaultdict

import yaml


def read_yaml(filename):
    with open(filename, "r") as file:
        return yaml.safe_load(file)


def write_yaml(data, filename):
    with open(filename, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


def get_prerequisites(course, catalog):
    return set(catalog.get(course, {}).get("requires", []))


def get_course_credits(course, catalog):
    return catalog.get(course, {}).get("credits", 0)


def verify_semester(semester, courses, taken_courses, catalog):
    if courses is None:
        return False, "Semester is empty"

    credits = sum(get_course_credits(course, catalog) for course in courses)

    if credits < 12:
        return False, f"{credits} credits is too few"
    elif credits > 21:
        return False, f"{credits} credits is too many"

    for course in courses:
        if course not in catalog:
            return False, f"{course} not found in catalogue"
        if course in taken_courses:
            return False, f"{course} already taken"
        prereqs = get_prerequisites(course, catalog)
        if not prereqs.issubset(taken_courses):
            return False, f"{course} requires {prereqs - taken_courses}"

    return True, f"Valid with {credits} credits"


def verify_schedule(schedule, catalog):
    taken = set()
    total_credits = 0

    for semester, courses in schedule.items():
        if courses is None:
            continue

        credits = sum(get_course_credits(course, catalog) for course in courses)

        if credits < 12:
            return False, f"{semester}: {credits} credits is too few"
        elif credits > 21:
            return False, f"{semester}: {credits} credits is too many"

        for course in courses:
            if course not in catalog:
                return False, f"{semester}: {course} not found in catalogue"
            if course in taken:
                return False, f"{semester}: {course} already taken"
            prereqs = get_prerequisites(course, catalog)
            if not prereqs.issubset(taken):
                return False, f"{semester}: {course} requires {prereqs - taken}"

        taken.update(courses)
        total_credits += credits

    if diff := set(catalog.keys()) - taken:
        missing_credits = sum(get_course_credits(course, catalog) for course in diff)
        return (
            False,
            f"Missing {len(diff)} courses worth {missing_credits} credits: {', '.join(diff)}",
        )

    return True, f"Valid schedule with {total_credits} total credits"


def generate_valid_schedule(catalog, initial_schedule, num_semesters=6):
    all_courses = set(catalog.keys())
    taken_courses = set()
    schedule = copy.deepcopy(initial_schedule)

    # Verify and keep pre-set semesters
    for semester, courses in list(schedule.items()):
        is_valid, message = verify_semester(semester, courses, taken_courses, catalog)
        if is_valid:
            taken_courses.update(courses)
            print(f"Keeping pre-set {semester}: {courses} - {message}")
        else:
            del schedule[semester]
            print(f"Removing invalid pre-set {semester}: {courses} - {message}")

    # Fill in missing semesters
    for i in range(1, num_semesters + 1):
        semester = f"Semester {i}"
        if semester not in schedule:
            schedule[semester] = []

    def backtrack(semester_index, count=[0]):
        if count[0] % 100000 == 0:
            print(f"Backtrack count: {count}")
            print(json.dumps(schedule, indent=2))
        count[0] += 1

        if semester_index == num_semesters:
            is_valid, message = verify_schedule(schedule, catalog)
            return is_valid

        semester = f"Semester {semester_index + 1}"
        if semester in initial_schedule and schedule[semester]:
            return backtrack(semester_index + 1)

        current_courses = schedule[semester]
        current_credits = sum(
            get_course_credits(course, catalog) for course in current_courses
        )

        if current_credits >= 12 and current_credits <= 21:
            if backtrack(semester_index + 1):
                return True

        available_courses = [
            course
            for course in all_courses - taken_courses
            if get_prerequisites(course, catalog).issubset(taken_courses)
        ]

        for course in available_courses:
            credits = get_course_credits(course, catalog)
            if current_credits + credits > 21:
                continue

            schedule[semester].append(course)
            taken_courses.add(course)

            if backtrack(semester_index):
                return True

            schedule[semester].remove(course)
            taken_courses.remove(course)

        return False

    if backtrack(0):
        return schedule
    else:
        return None


def main():
    catalog = read_yaml("catalogue.yaml")
    initial_schedule = read_yaml("schedule.yaml")

    print("Initial schedule:")
    print(json.dumps(initial_schedule, indent=2))

    valid_schedule = generate_valid_schedule(catalog, initial_schedule)

    if valid_schedule:
        is_valid, message = verify_schedule(valid_schedule, catalog)
        if is_valid:
            print("Valid schedule generated:")
            for semester, courses in valid_schedule.items():
                credits = sum(get_course_credits(course, catalog) for course in courses)
                print(f"{semester}: {courses} ({credits} credits)")

            write_yaml(valid_schedule, "generated_schedule.yaml")
            print("Schedule saved to 'generated_schedule.yaml'")
            print(message)
        else:
            print(f"Generated schedule is invalid: {message}")
    else:
        print("Unable to generate a valid schedule.")


if __name__ == "__main__":
    main()
