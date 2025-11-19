#!/usr/bin/env python3
"""
Jira Issue Field Validator for PPLWEBMYST Project
Validates issue fields against project-specific rules before creation/update
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime
import re


class JiraFieldValidator:
    """Validates Jira issue fields against PPLWEBMYST rules"""

    # Valid issue types in PPLWEBMYST
    VALID_TYPES = [
        "Épica",
        "Historia",
        "Task",
        "Bug",
        "Sub-task",
        "Initiative",
        "Spike",
        "Strategic Theme",
        "Design",
    ]

    # Valid workflow states
    VALID_STATES = [
        "Open",
        "Analyzing",
        "Backlog",
        "Ready to Start",
        "Prioritized",
        "In Progress",
        "Ready to Verify",
        "Deployed",
        "Closed",
        "Epic Refinement",
        "Discarded",
        "To deploy",
        "Delayed",
    ]

    # Valid priorities
    VALID_PRIORITIES = ["A++ (Bloqueo)", "A+ (Crítico)", "A (Muy Importante)", "B (Importante)", "C (Menor)", "D (Trivial)"]

    # Valid bug environments
    VALID_BUG_ENVIRONMENTS = ["Produccion", "Pre-produccion", "Testing", "Desarrollo"]

    # Issue type requirements
    REQUIRED_FIELDS = {
        "Épica": ["summary", "customfield_11762"],
        "Historia": ["summary"],
        "Task": ["summary"],
        "Bug": ["summary", "customfield_10824"],
        "Sub-task": ["summary", "parent"],
        "Initiative": ["summary"],
        "Spike": ["summary"],
        "Strategic Theme": ["summary"],
        "Design": ["summary"],
    }

    @staticmethod
    def validate_summary(summary: str) -> Tuple[bool, str]:
        """Validate summary field (1-200 chars, non-empty)"""
        if not summary or not isinstance(summary, str):
            return False, "Summary is required and must be a string"

        summary = summary.strip()
        if len(summary) < 1:
            return False, "Summary cannot be empty"
        if len(summary) > 200:
            return False, f"Summary exceeds 200 characters (current: {len(summary)})"

        return True, "Summary is valid"

    @staticmethod
    def validate_description(description: str) -> Tuple[bool, str]:
        """Validate description field (max 5000 chars)"""
        if description is None:
            return True, "Description is optional"

        if not isinstance(description, str):
            return False, "Description must be a string"

        if len(description) > 5000:
            return False, f"Description exceeds 5000 characters (current: {len(description)})"

        return True, "Description is valid"

    @staticmethod
    def validate_issue_type(issue_type: str) -> Tuple[bool, str]:
        """Validate issue type is supported"""
        if not issue_type or issue_type not in JiraFieldValidator.VALID_TYPES:
            valid = ", ".join(JiraFieldValidator.VALID_TYPES)
            return False, f"Invalid issue type. Must be one of: {valid}"

        # Prevent use of "Epic" (must use "Épica")
        if issue_type.lower() == "epic":
            return False, "Use 'Épica' not 'Epic' for issue type"

        return True, "Issue type is valid"

    @staticmethod
    def validate_priority(priority: str) -> Tuple[bool, str]:
        """Validate priority field"""
        if priority is None:
            return True, "Priority is optional"

        if priority not in JiraFieldValidator.VALID_PRIORITIES:
            valid = ", ".join(JiraFieldValidator.VALID_PRIORITIES)
            return False, f"Invalid priority. Must be one of: {valid}"

        return True, "Priority is valid"

    @staticmethod
    def validate_bug_environment(environment: str) -> Tuple[bool, str]:
        """Validate bug environment custom field"""
        if environment not in JiraFieldValidator.VALID_BUG_ENVIRONMENTS:
            valid = ", ".join(JiraFieldValidator.VALID_BUG_ENVIRONMENTS)
            return False, f"Invalid bug environment. Must be one of: {valid}"

        return True, "Bug environment is valid"

    @staticmethod
    def validate_duedate(duedate: str) -> Tuple[bool, str]:
        """Validate duedate field (YYYY-MM-DD format)"""
        if duedate is None:
            return True, "Duedate is optional"

        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, duedate):
            return False, f"Duedate must be in YYYY-MM-DD format (got: {duedate})"

        try:
            datetime.strptime(duedate, "%Y-%m-%d")
            return True, "Duedate is valid"
        except ValueError:
            return False, f"Invalid date: {duedate}"

    @staticmethod
    def validate_epic_name_match(summary: str, epic_name: str) -> Tuple[bool, str]:
        """For Épica type: customfield_11762 must exactly match summary"""
        if epic_name != summary:
            return False, f"Epic Name (customfield_11762) must exactly match summary. Summary: '{summary}', Epic Name: '{epic_name}'"

        return True, "Epic name matches summary"

    @staticmethod
    def validate_parent_issue_key(parent_key: str) -> Tuple[bool, str]:
        """Validate parent issue key format (PROJECT-NUMBER)"""
        pattern = r"^[A-Z]+-\d+$"
        if not re.match(pattern, parent_key):
            return False, f"Invalid parent issue key format: {parent_key}. Expected: PROJECT-NUMBER"

        return True, "Parent issue key format is valid"

    @staticmethod
    def validate_issue_fields(issue_data: Dict) -> Dict:
        """
        Comprehensive validation of all issue fields
        Returns: {"valid": bool, "errors": [], "warnings": []}
        """
        errors = []
        warnings = []

        issue_type = issue_data.get("issuetype", {})
        if isinstance(issue_type, dict):
            issue_type_name = issue_type.get("name")
        else:
            issue_type_name = str(issue_type)

        # Validate issue type first
        valid, msg = JiraFieldValidator.validate_issue_type(issue_type_name)
        if not valid:
            errors.append({"field": "issuetype", "error": msg})
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Validate required fields for this type
        required_fields = JiraFieldValidator.REQUIRED_FIELDS.get(issue_type_name, ["summary"])
        for field in required_fields:
            if field not in issue_data or not issue_data[field]:
                errors.append({"field": field, "error": f"Required field for {issue_type_name} type"})

        # Validate summary if present
        if "summary" in issue_data:
            valid, msg = JiraFieldValidator.validate_summary(issue_data["summary"])
            if not valid:
                errors.append({"field": "summary", "error": msg})

        # Validate description if present
        if "description" in issue_data:
            valid, msg = JiraFieldValidator.validate_description(issue_data["description"])
            if not valid:
                errors.append({"field": "description", "error": msg})

        # Validate priority if present
        if "priority" in issue_data:
            valid, msg = JiraFieldValidator.validate_priority(issue_data.get("priority", {}).get("name"))
            if not valid:
                errors.append({"field": "priority", "error": msg})

        # Type-specific validations
        if issue_type_name == "Épica":
            # Must have epic name matching summary
            epic_name = issue_data.get("customfield_11762")
            if epic_name:
                valid, msg = JiraFieldValidator.validate_epic_name_match(issue_data["summary"], epic_name)
                if not valid:
                    errors.append({"field": "customfield_11762", "error": msg})

        elif issue_type_name == "Bug":
            # Must have environment
            env = issue_data.get("customfield_10824")
            if env:
                valid, msg = JiraFieldValidator.validate_bug_environment(env)
                if not valid:
                    errors.append({"field": "customfield_10824", "error": msg})

        elif issue_type_name == "Sub-task":
            # Must have parent
            parent = issue_data.get("parent")
            if parent:
                parent_key = parent if isinstance(parent, str) else parent.get("key")
                valid, msg = JiraFieldValidator.validate_parent_issue_key(parent_key)
                if not valid:
                    errors.append({"field": "parent", "error": msg})

        # Validate duedate if present
        if "duedate" in issue_data:
            valid, msg = JiraFieldValidator.validate_duedate(issue_data["duedate"])
            if not valid:
                errors.append({"field": "duedate", "error": msg})

        # PPLWEBMYST-specific warnings
        if issue_type_name == "Bug" and "assignee" not in issue_data:
            warnings.append({"field": "assignee", "warning": "Bug must be assigned to QA team"})

        if "customfield_42960" not in issue_data and issue_data.get("status") == "Open":
            warnings.append({"field": "customfield_42960", "warning": "Consider populating Vertical Owner for classification"})

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "issue_type": issue_type_name,
        }


if __name__ == "__main__":
    # Example usage
    test_issue = {
        "summary": "Create mobile payment flow",
        "description": "Implement payment processing for mobile app",
        "issuetype": {"name": "Historia"},
        "priority": {"name": "A (Muy Importante)"},
    }

    result = JiraFieldValidator.validate_issue_fields(test_issue)
    print(json.dumps(result, indent=2))
