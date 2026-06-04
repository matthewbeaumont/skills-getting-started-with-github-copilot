import copy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


class TestApp:
    @staticmethod
    def _reset_activities():
        activities.clear()
        activities.update(copy.deepcopy(TestApp._original_activities))

    @classmethod
    def setup_class(cls):
        cls._original_activities = copy.deepcopy(activities)

    def setup_method(self):
        self._reset_activities()

    def test_get_activities_returns_activity_list(self):
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"

    def test_signup_for_activity_adds_participant(self):
        # Arrange
        activity_name = "Chess Club"
        new_email = "teststudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}

        activities_response = client.get("/activities").json()
        assert new_email in activities_response[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_unregister_participant_removes_participant(self):
        # Arrange
        activity_name = "Chess Club"
        participant_email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={participant_email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {participant_email} from {activity_name}"}

        activities_response = client.get("/activities").json()
        assert participant_email not in activities_response[activity_name]["participants"]

    def test_unregister_missing_participant_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        missing_email = "missingstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={missing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_root_redirects_to_static_index(self):
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
