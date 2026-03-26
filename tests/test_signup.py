"""
Tests for POST /activities/{activity_name}/signup endpoint using AAA (Arrange-Act-Assert) pattern
"""
import pytest


def test_successful_signup_to_activity(client):
    """
    Test that a student can successfully sign up for an activity
    
    Arrange: Activity exists with available spots, email not yet registered
    Act: POST to /activities/{activity_name}/signup with valid email
    Assert: Status 200, participant added to activity, success message returned
    """
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify participant was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_reject_duplicate_signup_for_same_activity(client):
    """
    Test that a student cannot sign up twice for the same activity
    
    Arrange: Student is already signed up for an activity
    Act: POST to /activities/{activity_name}/signup with same email
    Assert: Status 400, error message indicates already signed up
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up for Chess Club
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_reject_signup_for_nonexistent_activity(client):
    """
    Test that signup fails for non-existent activity
    
    Arrange: Activity name does not exist in database
    Act: POST to /activities/{activity_name}/signup for non-existent activity
    Assert: Status 404, error message indicates activity not found
    """
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_multiple_students_to_same_activity(client):
    """
    Test that multiple different students can sign up for the same activity
    
    Arrange: Activity exists, multiple emails ready to sign up
    Act: POST signup for activity with different emails sequentially
    Assert: All signups succeed, all participants are added
    """
    # Arrange
    activity_name = "Gym Class"
    new_students = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
    
    # Act & Assert for each student
    for email in new_students:
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"accept": "application/json"}
        )
        assert response.status_code == 200
    
    # Verify all participants were added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    activity_participants = activities[activity_name]["participants"]
    
    for email in new_students:
        assert email in activity_participants
    
    # Verify old participants are still there
    assert "john@mergington.edu" in activity_participants
    assert "olivia@mergington.edu" in activity_participants
