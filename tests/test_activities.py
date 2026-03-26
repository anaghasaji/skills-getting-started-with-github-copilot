"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern
"""
import pytest


def test_get_all_activities_returns_success(client):
    """
    Test that GET /activities returns all activities with correct structure
    
    Arrange: API is running with sample activities loaded via fixture
    Act: Send GET request to /activities
    Assert: Status 200, response contains all activities with required fields
    """
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Visual Arts",
        "Drama Club",
        "Debate Team",
        "Science Club"
    ]
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) == 9
    
    for activity_name in expected_activities:
        assert activity_name in activities
        activity = activities[activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


def test_get_activities_contains_correct_participant_counts(client):
    """
    Test that GET /activities returns correct participant information
    
    Arrange: Activities with known participants are loaded
    Act: Send GET request to /activities
    Assert: Participant counts match expected values
    """
    # Arrange
    expected_counts = {
        "Chess Club": 2,
        "Programming Class": 2,
        "Gym Class": 2,
        "Basketball Team": 1,
        "Tennis Club": 2,
        "Visual Arts": 1,
        "Drama Club": 2,
        "Debate Team": 1,
        "Science Club": 2
    }
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    
    for activity_name, expected_count in expected_counts.items():
        assert len(activities[activity_name]["participants"]) == expected_count
