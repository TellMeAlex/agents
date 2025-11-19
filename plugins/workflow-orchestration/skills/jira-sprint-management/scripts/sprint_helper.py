#!/usr/bin/env python3
"""
Jira Sprint Helper for PPLWEBMYST
Utilities for sprint planning, capacity calculation, and management
"""

import json
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from enum import Enum


class SprintState(Enum):
    """Sprint lifecycle states"""
    FUTURE = "FUTURE"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class SprintHelper:
    """Helper utilities for sprint operations"""

    # Standard sprint durations (in days)
    SPRINT_DURATIONS = {
        "1-week": 5,
        "2-week": 10,
        "3-week": 15,
        "4-week": 20,
    }

    @staticmethod
    def validate_sprint_name(name: str) -> Tuple[bool, str]:
        """Validate sprint name format"""
        if not name or not isinstance(name, str):
            return False, "Sprint name is required and must be a string"

        if len(name.strip()) == 0:
            return False, "Sprint name cannot be empty"

        if len(name) > 255:
            return False, f"Sprint name too long (max 255 chars, got {len(name)})"

        return True, "Sprint name is valid"

    @staticmethod
    def validate_sprint_goal(goal: str = None) -> Tuple[bool, str]:
        """Validate sprint goal"""
        if goal is None:
            return True, "Sprint goal is optional"

        if not isinstance(goal, str):
            return False, "Sprint goal must be a string"

        if len(goal) > 1000:
            return False, f"Sprint goal too long (max 1000 chars, got {len(goal)})"

        return True, "Sprint goal is valid"

    @staticmethod
    def validate_sprint_dates(start_date: str, end_date: str = None) -> Tuple[bool, str]:
        """Validate sprint date format (ISO 8601)"""
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False, f"Invalid start_date format: {start_date}. Use ISO 8601"

        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return False, f"Invalid end_date format: {end_date}. Use ISO 8601"

            if end <= start:
                return False, "end_date must be after start_date"

        return True, "Sprint dates are valid"

    @staticmethod
    def calculate_sprint_duration(start_date: str, end_date: str) -> int:
        """Calculate sprint duration in days"""
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            return (end - start).days
        except Exception:
            return 0

    @staticmethod
    def calculate_working_days(start_date: str, end_date: str, exclude_weekends: bool = True) -> int:
        """Calculate working days in sprint"""
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            working_days = 0
            current = start

            while current <= end:
                # Check if weekday (0-4 = Mon-Fri)
                if exclude_weekends:
                    if current.weekday() < 5:
                        working_days += 1
                else:
                    working_days += 1

                current += timedelta(days=1)

            return working_days
        except Exception:
            return 0

    @staticmethod
    def plan_sprint_dates(duration_key: str = "2-week") -> Dict:
        """Generate sprint dates based on duration"""
        duration_days = SprintHelper.SPRINT_DURATIONS.get(duration_key, 10)

        today = datetime.now()
        # Align to Monday
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=duration_days)

        return {
            "start_date": start_date.isoformat() + "Z",
            "end_date": end_date.isoformat() + "Z",
            "duration_days": duration_days,
            "working_days": SprintHelper.calculate_working_days(
                start_date.isoformat() + "Z",
                end_date.isoformat() + "Z"
            ),
        }

    @staticmethod
    def calculate_capacity(velocity: int, sprint_duration: int = 10, utilization: float = 0.8) -> int:
        """
        Calculate sprint capacity based on velocity
        velocity: average items/points per 10-day sprint
        utilization: team availability (0.8 = 80%)
        """
        if velocity <= 0:
            return 0

        # Adjust velocity for sprint duration
        velocity_per_day = velocity / 10.0
        base_capacity = velocity_per_day * sprint_duration

        # Apply utilization factor
        adjusted_capacity = int(base_capacity * utilization)

        return adjusted_capacity

    @staticmethod
    def calculate_velocity_buffer(planned_capacity: int, buffer_percent: float = 0.2) -> int:
        """Calculate safe capacity with buffer"""
        buffer = int(planned_capacity * buffer_percent)
        return planned_capacity - buffer

    @staticmethod
    def analyze_sprint_health(
        issues_total: int,
        issues_completed: int,
        issues_in_progress: int,
        sprint_days_total: int,
        sprint_days_elapsed: int,
    ) -> Dict:
        """
        Analyze sprint health and progress
        Returns health score and recommendations
        """
        if sprint_days_total == 0:
            return {"health": "UNKNOWN", "message": "Invalid sprint duration"}

        progress_percent = (sprint_days_elapsed / sprint_days_total) * 100
        completion_percent = (issues_completed / issues_total * 100) if issues_total > 0 else 0
        blocked_percent = ((issues_total - issues_completed - issues_in_progress) / issues_total * 100) if issues_total > 0 else 0

        # Expected completion at this point
        expected_completion = progress_percent

        # Health scoring
        if completion_percent >= expected_completion - 10:
            health = "HEALTHY"
            color = "green"
        elif completion_percent >= expected_completion - 25:
            health = "AT_RISK"
            color = "yellow"
        else:
            health = "CRITICAL"
            color = "red"

        # Recommendations
        recommendations = []
        if blocked_percent > 20:
            recommendations.append("High number of blocked issues - review blockers")
        if completion_percent < (progress_percent * 0.5):
            recommendations.append("Behind schedule - consider scope reduction or removing blockers")
        if issues_in_progress > issues_total * 0.4:
            recommendations.append("Too many WIP items - focus on completion over starting new")

        return {
            "health": health,
            "color": color,
            "progress_percent": round(progress_percent, 1),
            "completion_percent": round(completion_percent, 1),
            "blocked_percent": round(blocked_percent, 1),
            "on_track": completion_percent >= (expected_completion - 15),
            "recommendations": recommendations,
        }

    @staticmethod
    def plan_capacity_allocation(
        team_members: List[Dict], sprint_capacity: int
    ) -> Dict:
        """
        Allocate sprint capacity across team members
        team_members: [{"name": str, "capacity": int, "allocation": float}]
        """
        total_allocation = sum(m.get("allocation", 1.0) for m in team_members)

        allocations = {}
        for member in team_members:
            allocation_factor = member.get("allocation", 1.0) / total_allocation
            member_capacity = int(sprint_capacity * allocation_factor)
            allocations[member["name"]] = {
                "capacity": member_capacity,
                "allocation_percent": allocation_factor * 100,
            }

        return {
            "total_capacity": sprint_capacity,
            "allocations": allocations,
            "team_size": len(team_members),
        }

    @staticmethod
    def generate_sprint_summary(
        sprint_id: int,
        sprint_name: str,
        sprint_goal: str,
        total_issues: int,
        completed_issues: int,
        velocity: int,
        team_size: int,
    ) -> Dict:
        """Generate summary report for sprint"""
        completion_rate = (completed_issues / total_issues * 100) if total_issues > 0 else 0

        return {
            "sprint_id": sprint_id,
            "sprint_name": sprint_name,
            "sprint_goal": sprint_goal,
            "summary": {
                "total_issues": total_issues,
                "completed_issues": completed_issues,
                "incomplete_issues": total_issues - completed_issues,
                "completion_rate_percent": round(completion_rate, 1),
            },
            "team": {
                "size": team_size,
                "velocity": velocity,
                "average_per_person": round(velocity / team_size, 1) if team_size > 0 else 0,
            },
        }


class SprintTemplates:
    """Pre-built sprint templates"""

    @staticmethod
    def create_2week_sprint(sprint_number: int) -> Dict:
        """Create standard 2-week sprint"""
        dates = SprintHelper.plan_sprint_dates("2-week")

        return {
            "name": f"Sprint {sprint_number}",
            "goal": f"Define goal for Sprint {sprint_number}",
            "state": SprintState.FUTURE.value,
            "start_date": dates["start_date"],
            "end_date": dates["end_date"],
            "working_days": dates["working_days"],
        }

    @staticmethod
    def create_feature_sprint(sprint_number: int, feature_name: str) -> Dict:
        """Create sprint for specific feature"""
        template = SprintTemplates.create_2week_sprint(sprint_number)
        template["goal"] = f"Deliver {feature_name}"
        return template


if __name__ == "__main__":
    # Example usage
    print("=== Sprint Planning ===")
    dates = SprintHelper.plan_sprint_dates("2-week")
    print(json.dumps(dates, indent=2))

    print("\n=== Capacity Calculation ===")
    capacity = SprintHelper.calculate_capacity(velocity=30, sprint_duration=10, utilization=0.8)
    print(f"Planned capacity: {capacity} points")

    print("\n=== Sprint Health Analysis ===")
    health = SprintHelper.analyze_sprint_health(
        issues_total=20,
        issues_completed=10,
        issues_in_progress=5,
        sprint_days_total=10,
        sprint_days_elapsed=5,
    )
    print(json.dumps(health, indent=2))

    print("\n=== Team Capacity Allocation ===")
    team = [
        {"name": "Alice", "capacity": 1.0},
        {"name": "Bob", "capacity": 0.8},
        {"name": "Charlie", "capacity": 1.0},
    ]
    allocation = SprintHelper.plan_capacity_allocation(team, 24)
    print(json.dumps(allocation, indent=2))

    print("\n=== Sprint Template ===")
    sprint = SprintTemplates.create_2week_sprint(43)
    print(json.dumps(sprint, indent=2))
