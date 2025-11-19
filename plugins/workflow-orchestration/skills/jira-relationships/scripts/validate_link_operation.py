#!/usr/bin/env python3
"""
Jira Link Validator for PPLWEBMYST
Validates issue links before creation to prevent errors and circular dependencies
"""

import json
import re
from typing import Tuple, Dict, List


class LinkValidator:
    """Validates issue link operations"""

    # Valid link types
    VALID_LINK_TYPES = [
        "Blocks",
        "Relates to",
        "Duplicates",
        "Clones",
        "is part of",  # Epic link
    ]

    # Directional links (have outward/inward)
    DIRECTIONAL_LINKS = {
        "Blocks": {"outward": "blocks", "inward": "is blocked by"},
        "Relates to": {"outward": "relates to", "inward": "relates to"},
        "Duplicates": {"outward": "duplicates", "inward": "is duplicated by"},
        "Clones": {"outward": "clones", "inward": "is cloned by"},
        "is part of": {"outward": "is part of", "inward": "contains"},
    }

    @staticmethod
    def validate_issue_key_format(issue_key: str) -> Tuple[bool, str]:
        """Validate issue key format (PROJECT-NUMBER)"""
        pattern = r"^[A-Z]+-\d+$"
        if not re.match(pattern, issue_key):
            return False, f"Invalid issue key format: {issue_key}. Expected: PROJECT-NUMBER"

        return True, "Issue key format is valid"

    @staticmethod
    def validate_issue_key_project(issue_key: str, expected_project: str = "PPLWEBMYST") -> Tuple[bool, str]:
        """Validate issue key matches expected project"""
        project = issue_key.split("-")[0]
        if project != expected_project:
            return False, f"Issue {issue_key} is not in {expected_project} project"

        return True, f"Issue key {issue_key} is in {expected_project}"

    @staticmethod
    def validate_link_type(link_type: str) -> Tuple[bool, str]:
        """Validate link type is supported"""
        if link_type not in LinkValidator.VALID_LINK_TYPES:
            valid = ", ".join(LinkValidator.VALID_LINK_TYPES)
            return False, f"Invalid link type: {link_type}. Supported types: {valid}"

        return True, "Link type is valid"

    @staticmethod
    def validate_link_not_self(outward_key: str, inward_key: str) -> Tuple[bool, str]:
        """Prevent linking an issue to itself"""
        if outward_key.upper() == inward_key.upper():
            return False, f"Cannot link issue {outward_key} to itself"

        return True, "Issues are different"

    @staticmethod
    def validate_link_symmetry(link_type: str, is_directional_create: bool = True) -> Tuple[bool, str]:
        """Validate link type has proper symmetry"""
        link_info = LinkValidator.DIRECTIONAL_LINKS.get(link_type)
        if not link_info:
            return False, f"Link type {link_type} not found in directional links"

        # All our links are directional
        return True, "Link type has proper directional semantics"

    @staticmethod
    def validate_blocking_hierarchy(
        outward_key: str, inward_key: str, link_type: str, existing_links: List[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Prevent circular blocking dependencies
        existing_links: List of {"from": "KEY-1", "to": "KEY-2", "type": "Blocks"}
        """
        if link_type != "Blocks":
            return True, "Not a blocking link, no circular dependency check needed"

        if existing_links is None:
            existing_links = []

        # Build a map of existing blocking relationships
        blocking_map = {}
        for link in existing_links:
            if link.get("type") == "Blocks":
                from_key = link.get("from")
                to_key = link.get("to")
                if from_key not in blocking_map:
                    blocking_map[from_key] = []
                blocking_map[from_key].append(to_key)

        # Check if creating this link would create a cycle
        # Path: inward_key -> (existing links) -> outward_key
        # This would create: outward_key -> inward_key -> ... -> outward_key (cycle)

        def has_path(from_key: str, to_key: str, visited: set = None) -> bool:
            """Check if there's a path from from_key to to_key"""
            if visited is None:
                visited = set()

            if from_key in visited:
                return False

            if from_key == to_key:
                return True

            visited.add(from_key)
            for blocked_by in blocking_map.get(from_key, []):
                if has_path(blocked_by, to_key, visited):
                    return True

            return False

        # Check if creating outward -> inward would create a cycle
        if has_path(inward_key, outward_key):
            return False, f"Creating link would create circular dependency: {outward_key} -> {inward_key} -> ... -> {outward_key}"

        return True, "No circular dependencies detected"

    @staticmethod
    def validate_link_not_duplicate(
        outward_key: str, inward_key: str, link_type: str, existing_links: List[Dict] = None
    ) -> Tuple[bool, str]:
        """Prevent creating duplicate links"""
        if existing_links is None:
            existing_links = []

        for link in existing_links:
            if (
                link.get("from") == outward_key
                and link.get("to") == inward_key
                and link.get("type") == link_type
            ):
                return False, f"Link already exists: {outward_key} {link_type} {inward_key}"

        return True, "Link does not already exist"

    @staticmethod
    def validate_link_operation(
        outward_key: str, inward_key: str, link_type: str, existing_links: List[Dict] = None
    ) -> Dict:
        """
        Comprehensive validation of a link operation
        Returns: {"valid": bool, "errors": [], "warnings": []}
        """
        errors = []
        warnings = []

        # Validate outward issue key
        valid, msg = LinkValidator.validate_issue_key_format(outward_key)
        if not valid:
            errors.append({"field": "outward_key", "error": msg})

        valid, msg = LinkValidator.validate_issue_key_project(outward_key)
        if not valid:
            errors.append({"field": "outward_key", "error": msg})

        # Validate inward issue key
        valid, msg = LinkValidator.validate_issue_key_format(inward_key)
        if not valid:
            errors.append({"field": "inward_key", "error": msg})

        valid, msg = LinkValidator.validate_issue_key_project(inward_key)
        if not valid:
            errors.append({"field": "inward_key", "error": msg})

        # Validate link type
        valid, msg = LinkValidator.validate_link_type(link_type)
        if not valid:
            errors.append({"field": "link_type", "error": msg})
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Check for self-link
        valid, msg = LinkValidator.validate_link_not_self(outward_key, inward_key)
        if not valid:
            errors.append({"field": "link", "error": msg})

        # Check for circular dependencies (if blocking link)
        valid, msg = LinkValidator.validate_blocking_hierarchy(
            outward_key, inward_key, link_type, existing_links
        )
        if not valid:
            errors.append({"field": "link", "error": msg})

        # Check for duplicates
        valid, msg = LinkValidator.validate_link_not_duplicate(
            outward_key, inward_key, link_type, existing_links
        )
        if not valid:
            warnings.append({"field": "link", "warning": msg})

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "outward": outward_key,
            "inward": inward_key,
            "link_type": link_type,
        }


if __name__ == "__main__":
    # Example usage
    print("=== Valid Link ===")
    result = LinkValidator.validate_link_operation(
        "PPLWEBMYST-100", "PPLWEBMYST-101", "Blocks"
    )
    print(json.dumps(result, indent=2))

    print("\n=== Self-link Error ===")
    result = LinkValidator.validate_link_operation(
        "PPLWEBMYST-100", "PPLWEBMYST-100", "Relates to"
    )
    print(json.dumps(result, indent=2))

    print("\n=== Circular Dependency ===")
    existing = [
        {"from": "PPLWEBMYST-101", "to": "PPLWEBMYST-102", "type": "Blocks"},
        {"from": "PPLWEBMYST-102", "to": "PPLWEBMYST-100", "type": "Blocks"},
    ]
    result = LinkValidator.validate_link_operation(
        "PPLWEBMYST-100", "PPLWEBMYST-101", "Blocks", existing
    )
    print(json.dumps(result, indent=2))

    print("\n=== Duplicate Link ===")
    existing = [
        {"from": "PPLWEBMYST-100", "to": "PPLWEBMYST-101", "type": "Relates to"}
    ]
    result = LinkValidator.validate_link_operation(
        "PPLWEBMYST-100", "PPLWEBMYST-101", "Relates to", existing
    )
    print(json.dumps(result, indent=2))
