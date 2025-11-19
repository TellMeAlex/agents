#!/usr/bin/env python3
"""
JQL Query Builder for PPLWEBMYST
Builds valid JQL queries from filter parameters
"""

import json
from typing import Dict, List, Optional
from urllib.parse import quote


class JQLBuilder:
    """Builds JQL queries for Jira PPLWEBMYST project"""

    def __init__(self):
        self.conditions = []
        self.project = "PPLWEBMYST"

    def add_condition(self, field: str, operator: str, value) -> "JQLBuilder":
        """Add a condition to the query"""
        if isinstance(value, str):
            # Quote string values, handle special cases
            if field in ["status", "priority", "type"]:
                value = f'"{value}"'
            elif " " in str(value):
                value = f'"{value}"'
        elif isinstance(value, list):
            # Handle IN operator
            quoted_values = [f'"{v}"' if isinstance(v, str) else str(v) for v in value]
            value = f"({', '.join(quoted_values)})"
            operator = "IN"

        condition = f"{field} {operator} {value}"
        self.conditions.append(condition)
        return self

    def status(self, status: str) -> "JQLBuilder":
        """Filter by status"""
        return self.add_condition("status", "=", status)

    def status_in(self, statuses: List[str]) -> "JQLBuilder":
        """Filter by multiple statuses"""
        return self.add_condition("status", "IN", statuses)

    def issue_type(self, issue_type: str) -> "JQLBuilder":
        """Filter by issue type"""
        return self.add_condition("type", "=", issue_type)

    def issue_types(self, types: List[str]) -> "JQLBuilder":
        """Filter by multiple issue types"""
        return self.add_condition("type", "IN", types)

    def assignee(self, user_email: str) -> "JQLBuilder":
        """Filter by assignee"""
        return self.add_condition("assignee", "=", user_email)

    def unassigned(self) -> "JQLBuilder":
        """Filter unassigned issues"""
        self.conditions.append("assignee IS EMPTY")
        return self

    def priority(self, priority: str) -> "JQLBuilder":
        """Filter by priority"""
        return self.add_condition("priority", "=", priority)

    def priorities(self, priorities: List[str]) -> "JQLBuilder":
        """Filter by multiple priorities"""
        return self.add_condition("priority", "IN", priorities)

    def sprint(self, sprint_id_or_name) -> "JQLBuilder":
        """Filter by sprint"""
        return self.add_condition("sprint", "=", sprint_id_or_name)

    def no_sprint(self) -> "JQLBuilder":
        """Filter issues not in any sprint"""
        self.conditions.append("sprint IS EMPTY")
        return self

    def label(self, label: str) -> "JQLBuilder":
        """Filter by label"""
        return self.add_condition("labels", "=", label)

    def component(self, component: str) -> "JQLBuilder":
        """Filter by component"""
        return self.add_condition("components", "=", component)

    def due_date_before(self, date: str) -> "JQLBuilder":
        """Filter issues with duedate before date (YYYY-MM-DD)"""
        return self.add_condition("duedate", "<", date)

    def due_date_after(self, date: str) -> "JQLBuilder":
        """Filter issues with duedate after date (YYYY-MM-DD)"""
        return self.add_condition("duedate", ">", date)

    def due_date_overdue(self) -> "JQLBuilder":
        """Filter overdue issues"""
        self.conditions.append("duedate < now()")
        self.conditions.append("status != Closed")
        return self

    def created_after(self, days: int) -> "JQLBuilder":
        """Filter recently created issues"""
        self.conditions.append(f"created >= -{days}d")
        return self

    def updated_after(self, days: int) -> "JQLBuilder":
        """Filter recently updated issues"""
        self.conditions.append(f"updated >= -{days}d")
        return self

    def custom_field(self, field_id: str, operator: str, value) -> "JQLBuilder":
        """Add custom field filter (e.g., customfield_10824 = "Produccion")"""
        if isinstance(value, str) and " " in value:
            value = f'"{value}"'
        condition = f"{field_id} {operator} {value}"
        self.conditions.append(condition)
        return self

    def bug_environment(self, environment: str) -> "JQLBuilder":
        """Filter by bug environment (customfield_10824)"""
        return self.custom_field("customfield_10824", "=", environment)

    def vertical_owner(self, owner: str) -> "JQLBuilder":
        """Filter by vertical owner (customfield_42960)"""
        return self.custom_field("customfield_42960", "=", owner)

    def no_vertical_owner(self) -> "JQLBuilder":
        """Filter issues without vertical owner"""
        self.conditions.append("customfield_42960 IS EMPTY")
        return self

    def text_search(self, text: str) -> "JQLBuilder":
        """Search in text fields"""
        self.conditions.append(f'text ~ "{text}"')
        return self

    def linked_to_epic(self, epic_key: str) -> "JQLBuilder":
        """Filter issues linked to epic"""
        self.conditions.append(f'customfield_10100 = "{epic_key}"')
        return self

    def order_by(self, field: str, direction: str = "ASC") -> "JQLBuilder":
        """Set ordering (use at the end)"""
        self.order_clause = f"ORDER BY {field} {direction}"
        return self

    def build(self) -> str:
        """Build and return the complete JQL query"""
        # Always start with project
        query = f"project = {self.project}"

        # Add all conditions
        if self.conditions:
            query += " AND " + " AND ".join(self.conditions)

        # Add ordering if specified
        if hasattr(self, "order_clause"):
            query += f" {self.order_clause}"

        return query

    def build_url_encoded(self) -> str:
        """Build JQL query and URL-encode it"""
        return quote(self.build())

    def reset(self) -> "JQLBuilder":
        """Reset builder for new query"""
        self.conditions = []
        if hasattr(self, "order_clause"):
            del self.order_clause
        return self


# Common query templates
class JQLTemplates:
    """Pre-built common queries for PPLWEBMYST"""

    @staticmethod
    def my_open_issues(user_email: str) -> str:
        """Issues assigned to me that are open"""
        return (
            JQLBuilder()
            .assignee(user_email)
            .status_in(["Open", "In Progress", "Ready to Start"])
            .build()
        )

    @staticmethod
    def unassigned_bugs() -> str:
        """All unassigned bugs"""
        return JQLBuilder().issue_type("Bug").unassigned().build()

    @staticmethod
    def bugs_in_production() -> str:
        """Bugs reported in production"""
        return JQLBuilder().issue_type("Bug").bug_environment("Produccion").build()

    @staticmethod
    def current_sprint_backlog() -> str:
        """Current sprint issues ready to start"""
        return (
            JQLBuilder()
            .sprint("openSprints")
            .status_in(["Ready to Start", "Backlog"])
            .order_by("priority", "DESC")
            .build()
        )

    @staticmethod
    def overdue_issues() -> str:
        """Overdue unresolved issues"""
        return JQLBuilder().due_date_overdue().order_by("duedate", "ASC").build()

    @staticmethod
    def recently_updated(days: int = 7) -> str:
        """Issues updated in last N days"""
        return JQLBuilder().updated_after(days).order_by("updated", "DESC").build()

    @staticmethod
    def issues_without_owner() -> str:
        """Issues missing vertical owner"""
        return JQLBuilder().no_vertical_owner().order_by("created", "DESC").build()

    @staticmethod
    def by_epic(epic_key: str) -> str:
        """All issues in an epic"""
        return (
            JQLBuilder()
            .linked_to_epic(epic_key)
            .order_by("type", "ASC")
            .build()
        )


if __name__ == "__main__":
    # Example usage
    print("=== Basic Query ===")
    builder = JQLBuilder()
    query = builder.status("In Progress").assignee("alejandro@example.com").build()
    print(query)

    print("\n=== Complex Query ===")
    builder.reset()
    query = (
        builder.issue_type("Bug")
        .bug_environment("Produccion")
        .status("Open")
        .order_by("priority", "DESC")
        .build()
    )
    print(query)

    print("\n=== Template Query ===")
    query = JQLTemplates.overdue_issues()
    print(query)

    print("\n=== URL Encoded ===")
    builder.reset()
    encoded = builder.issue_type("Historia").unassigned().build_url_encoded()
    print(encoded)
