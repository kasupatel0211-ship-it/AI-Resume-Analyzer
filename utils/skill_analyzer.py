SKILLS = [
    "python",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "sql",
    "flask",
    "django",
    "git",
    "excel",
    "machine learning",
    "data analysis"
]


def detect_skills(text):

    text = text.lower()

    found = []

    for skill in SKILLS:

        if skill in text:
            found.append(skill)

    return found


def missing_skills(skills):

    return list(
        set(SKILLS) - set(skills)
    )