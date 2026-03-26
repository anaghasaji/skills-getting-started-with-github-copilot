"""
Tests for POST /activities/{activity_name}/unregister endpoint using AAA (Arrange-Act-Assert) pattern
"""
import pytest


def test_successful_unregister_from_activity(client):
    """
    Test that a participant can successfully unregister from an activity
    
    Arrange: Participant is registered for an activity
    Act: POST to /activities/{activity_name}/unregister with participant email
    Assert: Status 200, participant removed from activity, success message returned
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already a participant
    
    # Verify participant exists before unregister
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify participant was actually removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_reject_unregister_of_non_participant(client):
    """
    Test that unregister fails for non-registered participant
    
    Arrange: Email is not registered for the activity
    Act: POST to /activities/{activity_name}/unregister with non-participant email
    Assert: Status 400, error message indicates not signed up
    """
    # Arrange
    activity_name = "Chess Club"
    email = "nonparticipant@mergington.edu"  # Not a participant
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()


def test_reject_unregister_from_nonexistent_activity(client):
    """
    Test that unregister fails for non-existent activity
    
    Arrange: Activity name does not exist in database
    Act: POST to /activities/{activity_name}/unregister for non-existent activity
    Assert: Status 404, error message indicates activity not found
    """
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_and_re_signup_same_participant(client):
    """
    Test that a participant can unregister and then re-signup for an activity
    
    Arrange: Participant is registered for an activity
    Act: Unregister participant, then signup again
    Assert: Both operations succeed, participant is re-added to activity
    """
    # Arrange
    activity_name = "Drama Club"
    email = "newestudent@mergington.edu"
    
    # First signup
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    assert signup_response.status_code == 200
    
    # Verify registered
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]
    
    # Act - Unregister
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )
    assert unregister_response.status_code == 200
    
    # Verify unregistered
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]
    
    # Re-signup
    re_signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )
    assert re_signup_response.status_code == 200
    
    # Verify re-registered
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]


def test_unregister_one_participant_keeps_others(client):
    """
    Test that unregistering one participant doesn't affect others
    
    Arrange: Activity has multiple participants
    Act: Unregister one participant
    Assert: Other participants remain registered
    """
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    email_to_keep = "daniel@mergington.edu"
    
    # Verify both are registered
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email_to_remove in participants
    assert email_to_keep in participants
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister?email={email_to_remove}",
        headers={"accept": "application/json"}
    )
    
    # Assert
    assert response.status_code == 200
    
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email_to_remove not in participants
    assert email_to_keep in participants
