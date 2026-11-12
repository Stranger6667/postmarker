---
name: Bug report
about: Create a report to help us improve
title: "[BUG]"
labels: 'Status: Review Needed, Type: Bug'
assignees: Stranger6667

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
A minimal code example that reproduces the problem, and the full traceback if there is one.
Replace API tokens and email addresses with placeholders.

```python
from postmarker.core import PostmarkClient

postmark = PostmarkClient(server_token="SERVER_TOKEN")
...
```

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment (please complete the following information):**

- OS: [e.g. Linux or Windows]
- Python version: [e.g. 3.13.1]
- Postmarker version: [e.g. 1.0]
- Django version, if you use the Django email backend: [e.g. 5.2.8]

**Additional context**
Add any other context about the problem here, e.g. Postmark's error code and message.
