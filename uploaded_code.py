import pycodestyle

def check_pep8_compliance(file_path):
    style = pycodestyle.StyleGuide()
    report = style.check_files([file_path])

    if report.total_errors == 0:
        return "Code is PEP8 compliant!"

    issues = []
    for line in report.get_statistics():
        issues.append(line)

    return f"Found {report.total_errors} PEP8 issues:\n" + "\n".join(issues)

