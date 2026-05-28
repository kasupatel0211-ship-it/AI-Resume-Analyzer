def is_resume(text):

    resume_keywords = [
        "education",
        "skills",
        "experience",
        "projects",
        "certifications",
        "objective",
        "internship",
        "work experience",
        "technical skills",
        "resume"
    ]

    text = text.lower()

    count = 0

    for keyword in resume_keywords:
        if keyword in text:
            count += 1

    return count >= 3