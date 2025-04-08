# Given courses data
courses = {
    "PSYC 1101": {
        "name": "General Psychology",
        "credits": 3,
        "requirements": [],
    },
    "CS 2051": {
        "name": "Honors Discrete Math",
        "credits": 3,
        "requirements": [],
    },
    "CS 1332": {
        "name": "Data Structures and Algorithms",
        "credits": 3,
        "requirements": [],
    },
    "MATH 2561": {
        "name": "Honors Multivariable Calculus",
        "credits": 4,
        "requirements": [],
    },
    "CS 2340": {"name": "Objects and Design", "credits": 3, "requirements": []},
    "CS 4003": {
        "name": "AI Ethics and Society",
        "credits": 3,
        "requirements": [],
    },
    "CS 2110": {
        "name": "Computer Organization and Programming",
        "credits": 4,
        "requirements": [],
    },
    "CS 2200": {
        "name": "Systems and Networks",
        "credits": 4,
        "requirements": ["CS 2110"],
    },
    "CS 3210": {
        "name": "Design of Operating Systems",
        "credits": 3,
        "requirements": ["CS 2200"],
    },
    "CS 3220": {
        "name": "Processor Design",
        "credits": 3,
        "requirements": ["CS 2200"],
    },
    "CS 3511": {
        "name": "Algorithms Honors",
        "credits": 3,
        "requirements": ["CS 2051", "CS 1332"],
    },
    "ECE 2031": {
        "name": "Digital Design Laboratory",
        "credits": 2,
        "requirements": ["CS 2110"],
    },
    "CS 3600": {
        "name": "Intro to Artificial Intelligence",
        "credits": 3,
        "requirements": ["CS 1332"],
    },
    "CS 3630": {
        "name": "Intro to Perception and Robotics",
        "credits": 3,
        "requirements": ["CS 1332"],
    },
    "CS 4641": {
        "name": "Machine Learning",
        "credits": 3,
        "requirements": ["CS 1332"],
    },
    "CS 4644": {
        "name": "Deep Learning",
        "credits": 3,
        "requirements": ["MATH 2561", "CS 2110", "CS 3511"],
    },
    "CS 4650": {
        "name": "Natural Language",
        "credits": 3,
        "requirements": ["CS 3511", "MATH 2561"],
    },
    "CS 4240": {
        "name": "Compilers and Interpreters",
        "credits": 3,
        "requirements": ["CS 2340"],
    },
    "MATH 3012": {
        "name": "Applied Combinatorics",
        "credits": 3,
        "requirements": ["CS 2051"],
    },
    "MATH 3215": {
        "name": "Probability and Statistics",
        "credits": 3,
        "requirements": ["MATH 2561"],
    },
}

# Number of semesters
num_semesters = 5


def can_schedule(course, semester, schedule, courses):
    """Check if a course can be scheduled in the given semester."""
    # Check if prerequisites are satisfied
    for req in courses[course]["requirements"]:
        if req not in schedule or schedule[req] >= semester:
            return False
    return True


def backtrack(schedule, semester, courses, num_semesters):
    print(schedule)
    print()
    """Backtracking algorithm to find all valid schedules."""
    # Base case: If all courses have been scheduled
    if len(schedule) == len(courses):
        return [schedule.copy()]

    # Recursive case
    schedules = []
    for course in courses:
        if course not in schedule:
            for sem in range(semester, num_semesters):
                if can_schedule(course, sem, schedule, courses):
                    schedule[course] = sem
                    schedules += backtrack(
                        schedule, semester, courses, num_semesters
                    )
                    del schedule[course]
    return schedules


# Generate all possible schedules
schedules = backtrack({}, 0, courses, num_semesters)

# Show the number of valid schedules found
len(schedules), schedules[:3]  # Displaying the first 3 schedules as an example
