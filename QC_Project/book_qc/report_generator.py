def calculate_score(structural, typography, semantic):
    score = 100
    score -= len(structural) * 3
    score -= len(typography) * 2
    score -= len(semantic) * 2
    return max(score, 0)


def generate_report(structural, typography, semantic):
    score = calculate_score(structural, typography, semantic)

    if score >= 85:
        status = "Ready for Publishing"
    elif score >= 70:
        status = "Minor Revisions Required"
    else:
        status = "Major Revisions Required"

    report = "BOOK QUALITY CONTROL REPORT\n"
    report += "=" * 50 + "\n\n"

    # STRUCTURAL
    report += f"STRUCTURAL ISSUES ({len(structural)}):\n"
    for issue in structural:
        report += f"- [{issue['severity']}] {issue['message']}\n"

    # TYPOGRAPHY
    report += f"\nTYPOGRAPHY ISSUES ({len(typography)}):\n"
    for issue in typography:
        report += f"- [{issue['severity']}] {issue['message']}\n"

    # SEMANTIC
    report += f"\nSEMANTIC ISSUES ({len(semantic)}):\n"
    for issue in semantic:
        report += f"- [{issue['severity']}] {issue['message']}\n"

    report += f"\nOVERALL SCORE: {score}/100\n"
    report += f"STATUS: {status}\n"

    return report, score, status