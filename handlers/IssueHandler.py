class IssueHandler:
    def __init__(self, issues):
        self.issues = issues

    def display_issues(self):
        for issue in self.issues:
            print(f'#{issue["number"]}: {issue["title"]}')

    def select_issue(self):
        while True:
            issue_number_input = input(
                "\nEnter the issue number you want to view (0 to exit): "
            )
            try:
                selected_issue_number = int(issue_number_input)
                if selected_issue_number == 0:
                    return None

                selected_issue = next(
                    (issue for issue in self.issues if issue["number"] == selected_issue_number),
                    None,
                )

                if selected_issue:
                    return selected_issue
                else:
                    print("Invalid issue number.")
            except ValueError:
                print(f"Invalid input: {issue_number_input}. Please enter a valid issue number.")
