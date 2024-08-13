from collections import defaultdict

import yaml


def build_graph(courses):
    graph = defaultdict(list)
    for course, data in courses.items():
        for prereq in data.get("requires", []):
            graph[prereq].append(course)
    return graph


def count_ancestors(graph, node, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return 0
    visited.add(node)
    count = 1  # Count the node itself
    for child in graph[node]:
        count += count_ancestors(graph, child, visited)
    return count


def sort_courses_by_ancestors(courses, graph):
    course_ancestors = {
        course: count_ancestors(graph, course)
        - 1  # Subtract 1 to exclude the course itself
        for course in courses
    }
    return sorted(course_ancestors.items(), key=lambda x: x[1], reverse=True)


def read_yaml(filename):
    try:
        with open(filename, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{filename}': {e}")
        exit(1)


# Main execution
courses = read_yaml("catalogue.yaml")
schedule = read_yaml("full_schedule.yaml")

# Extract all scheduled courses
scheduled_courses = set()
for semester, courses_list in schedule.items():
    scheduled_courses.update(courses_list)

graph = build_graph(courses)
sorted_courses = sort_courses_by_ancestors(courses, graph)

print("Scheduled courses:", scheduled_courses)
print(
    "\nCourses sorted by number of ancestors (prerequisites), excluding scheduled courses:"
)
for course, ancestor_count in sorted_courses:
    # if course not in scheduled_courses:
    print(f"{course}: {ancestor_count} ancestors")
