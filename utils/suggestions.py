def generate_suggestions(skills, text):

    suggestions = []

    if "github" not in text:
        suggestions.append(
            "Add GitHub Profile"
        )

    if "linkedin" not in text:
        suggestions.append(
            "Add LinkedIn Profile"
        )

    if "internship" not in text:
        suggestions.append(
            "Add Internship Experience"
        )

    if "project" not in text:
        suggestions.append(
            "Add More Projects"
        )

    if "certification" not in text:
        suggestions.append(
            "Add Certifications"
        )

    return suggestions