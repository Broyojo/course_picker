import copy

from schedule import intel_systems_courses


def find_root_courses(courses):
    root_courses = []
    for course, details in courses.items():
        if not details["requirements"]:
            root_courses.append(course)
    return root_courses


def find_next_courses(courses, done_courses):
    next_courses = []
    for course, details in courses.items():
        if all(requirement in done_courses for requirement in details["requirements"]):
            if course not in done_courses:
                next_courses.append(course)
    return next_courses


def generate_schedule(courses, done_courses=None, schedule=None, semester=1):
    if done_courses is None:
        done_courses = set()
    if schedule is None:
        schedule = {}

    if semester > 8:  # Assuming a 4-year (8 semester) schedule
        if verify(schedule):
            return schedule
        else:
            return None

    # Try to fill the semester with courses
    for course in find_root_courses(courses) + find_next_courses(courses, done_courses):
        if semester not in schedule:
            schedule[semester] = []

        # Check if adding this course would exceed the credit limit
        current_credits = sum(courses[c]["credits"] for c in schedule[semester])
        if current_credits + courses[course]["credits"] > 21:
            continue

        # Add course to schedule
        schedule[semester].append(course)
        done_courses.add(course)

        # Recursively try to fill the next semesters
        new_schedule = generate_schedule(
            courses, done_courses, copy.deepcopy(schedule), semester
        )
        if new_schedule:
            return new_schedule

        # If adding this course didn't lead to a valid schedule, remove it and try the next one
        schedule[semester].remove(course)
        done_courses.remove(course)

    # If this semester is not filled yet, move on to the next one
    return generate_schedule(courses, done_courses, schedule, semester + 1)


def verify(schedule):
    """
    Check that all the requirements are met and that
    number of credits per semester is >= 12 and <= 21
    """

    done_courses = set()

    total_credits = 0

    valid = True

    for i, semester in schedule.items():
        credits = 0

        for course in semester:
            if course in done_courses:
                print(f"Invalid schedule, {course} has already been taken.")
                valid = False
            requirements = intel_systems_courses[course]["requirements"]
            for requirement in requirements:
                if requirement not in done_courses:
                    print(
                        f"Invalid schedule, {course} requires {requirement} which has not been taken."
                    )
                    valid = False
            credits += intel_systems_courses[course]["credits"]

        for course in semester:
            done_courses.add(course)

        if credits < 12 or credits > 21:
            print(
                f"Invalid schedule, {credits} credits is too few credits for semester {i}."
            )
            valid = False
        else:
            print(f"Semester {i} is valid with {credits} credits.")

        total_credits += credits

    missing_courses = set(intel_systems_courses.keys()).difference(done_courses)
    if len(missing_courses) != 0:
        print(f"Missing courses: {missing_courses}")
        valid = False

    print(
        f"Total credits: {total_credits} + 55 = {total_credits + 55}. Missing {126 - total_credits - 55} credits."
    )

    return valid


# Usage
schedule = generate_schedule(intel_systems_courses)
if schedule:
    print("Valid Schedule Found:")
    for semester, intel_systems_courses in schedule.items():
        print(f"Semester {semester}: {intel_systems_courses}")
else:
    print("No valid schedule found")
