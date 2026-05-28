def calculate_score(skills, text):

    score = 0

    text = text.lower()

    # ======================
    # SKILLS SCORE
    # ======================
    score += len(skills) * 5

    # ======================
    # EDUCATION
    # ======================
    education_keywords = [
        "bachelor",
        "master",
        "b.tech",
        "m.tech",
        "bca",
        "mca",
        "degree",
        "university",
        "college"
    ]

    for word in education_keywords:

        if word in text:
            score += 5
            break

    # ======================
    # PROJECTS
    # ======================
    project_keywords = [
        "project",
        "projects",
        "developed",
        "built",
        "created"
    ]

    for word in project_keywords:

        if word in text:
            score += 10
            break

    # ======================
    # EXPERIENCE
    # ======================
    experience_keywords = [
        "experience",
        "internship",
        "worked",
        "company",
        "organization"
    ]

    for word in experience_keywords:

        if word in text:
            score += 10
            break

    # ======================
    # CERTIFICATIONS
    # ======================
    certification_keywords = [
        "certification",
        "certificate",
        "course",
        "training"
    ]

    for word in certification_keywords:

        if word in text:
            score += 10
            break

    # ======================
    # CONTACT INFO
    # ======================
    if "@" in text:
        score += 5

    if "+91" in text or "phone" in text:
        score += 5

    # ======================
    # LINKEDIN / GITHUB
    # ======================
    if "linkedin" in text:
        score += 5

    if "github" in text:
        score += 5

    # ======================
    # RESUME LENGTH
    # ======================
    word_count = len(text.split())

    if word_count > 300:
        score += 10

    # ======================
    # LIMIT SCORE
    # ======================
    if score > 100:
        score = 100

    return score