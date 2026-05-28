JOB_ROLES = {

    "Python Developer": [
        "python",
        "flask",
        "django",
        "sql",
        "git"
    ],

    "Web Developer": [
        "html",
        "css",
        "javascript",
        "sql",
        "git"
    ],

    "Data Analyst": [
        "python",
        "sql",
        "data analysis",
        "excel"
    ]
}


def match_job_role(skills):

    best_role = "General Candidate"
    best_score = 0

    for role, role_skills in JOB_ROLES.items():

        matched = len(
            set(skills) &
            set(role_skills)
        )

        if matched > best_score:

            best_score = matched
            best_role = role

    return best_role