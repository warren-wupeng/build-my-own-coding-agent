# SOP: New Feature Request Processing

PM agent follows this procedure when a user requests a new feature.

## Prerequisites

- User has provided a clear feature description
- Project repository is initialized

## Steps

1. Analyze user request
   - Action: Read the user's feature description and identify key requirements
   - Tool: read_file
   - Check: Requirements list is complete and unambiguous

2. Create issues for the feature
   - Action: Break down the feature into implementable issues
   - Tool: create_issue
   - Check: Each issue has clear acceptance criteria

3. Assign issues to engineer
   - Action: Assign implementation issues to the engineer agent
   - Tool: assign_task
   - Check: Engineer has acknowledged the assignment

4. Monitor progress
   - Action: Periodically check issue status and engineer messages
   - Tool: check_progress
   - Check: All issues are progressing within expected timeline

5. Review and accept delivery
   - Action: Review completed work against acceptance criteria
   - Tool: read_file
   - Check: All acceptance criteria met, tests passing
