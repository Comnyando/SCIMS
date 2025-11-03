"""
Tests for Commons API endpoints.
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models.commons_submission import CommonsSubmission
from app.models.commons_entity import CommonsEntity
from app.models.commons_moderation_action import CommonsModerationAction
from app.models.tag import Tag
from app.models.user import User


class TestCommonsSubmission:
    """Tests for commons submission endpoints."""

    def test_create_submission(
        self, client, auth_headers, test_user, db_session
    ):
        """Test creating a new submission."""
        submission_data = {
            "entity_type": "item",
            "entity_payload": {
                "name": "Test Quantum Drive",
                "description": "A test quantum drive",
                "category": "Components",
            },
            "source_reference": "https://example.com/test",
        }

        response = client.post(
            "/api/v1/commons/submit",
            json=submission_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["entity_type"] == "item"
        assert data["status"] == "pending"
        assert data["submitter_id"] == test_user.id

        # Verify in database
        submission = (
            db_session.query(CommonsSubmission)
            .filter(CommonsSubmission.id == data["id"])
            .first()
        )
        assert submission is not None
        assert submission.entity_payload["name"] == "Test Quantum Drive"

    def test_get_my_submissions(
        self, client, auth_headers, test_user, db_session
    ):
        """Test getting current user's submissions."""
        # Create a submission
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Test Item"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()

        response = client.get(
            "/api/v1/commons/my-submissions",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["submissions"]) >= 1
        assert any(sub["id"] == str(submission.id) for sub in data["submissions"])

    def test_update_submission(
        self, client, auth_headers, test_user, db_session
    ):
        """Test updating a pending submission."""
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Original Name"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        update_data = {
            "entity_payload": {"name": "Updated Name"},
            "source_reference": "https://example.com/updated",
        }

        response = client.patch(
            f"/api/v1/commons/submissions/{submission.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["entity_payload"]["name"] == "Updated Name"
        assert data["source_reference"] == "https://example.com/updated"

    def test_update_submission_wrong_user(
        self, client, auth_headers, test_user, other_user, db_session
    ):
        """Test that users cannot update other users' submissions."""
        submission = CommonsSubmission(
            submitter_id=other_user.id,
            entity_type="item",
            entity_payload={"name": "Other User's Item"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        update_data = {"entity_payload": {"name": "Hacked Name"}}

        response = client.patch(
            f"/api/v1/commons/submissions/{submission.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_submission_not_pending(
        self, client, auth_headers, test_user, db_session
    ):
        """Test that non-pending submissions cannot be updated."""
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Approved Item"},
            status="approved",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        update_data = {"entity_payload": {"name": "Updated Name"}}

        response = client.patch(
            f"/api/v1/commons/submissions/{submission.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAdminCommonsModeration:
    """Tests for admin moderation endpoints."""

    def test_list_submissions(
        self, client, auth_headers, test_user, db_session
    ):
        """Test listing submissions for moderation."""
        # Create a submission
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Test Item"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()

        response = client.get(
            "/api/v1/admin/commons/submissions",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["submissions"]) >= 1

    def test_approve_submission(
        self, client, auth_headers, test_user, db_session
    ):
        """Test approving a submission and creating a commons entity."""
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Test Item", "description": "Test"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        action_data = {
            "action": "approve",
            "notes": "Looks good, approved",
        }

        response = client.post(
            f"/api/v1/admin/commons/submissions/{submission.id}/approve",
            json=action_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "approved"

        # Verify commons entity was created
        entity = (
            db_session.query(CommonsEntity)
            .filter(CommonsEntity.entity_type == "item")
            .first()
        )
        assert entity is not None
        assert entity.is_public is True
        assert entity.data["name"] == "Test Item"

        # Verify moderation action was logged
        action = (
            db_session.query(CommonsModerationAction)
            .filter(CommonsModerationAction.submission_id == submission.id)
            .first()
        )
        assert action is not None
        assert action.action == "approve"

    def test_reject_submission(
        self, client, auth_headers, test_user, db_session
    ):
        """Test rejecting a submission."""
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Bad Item"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        action_data = {
            "action": "reject",
            "notes": "Does not meet quality standards",
        }

        response = client.post(
            f"/api/v1/admin/commons/submissions/{submission.id}/reject",
            json=action_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "rejected"

        # Verify no commons entity was created
        entity = (
            db_session.query(CommonsEntity)
            .filter(CommonsEntity.entity_type == "item")
            .first()
        )
        assert entity is None

    def test_request_changes(
        self, client, auth_headers, test_user, db_session
    ):
        """Test requesting changes on a submission."""
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Incomplete Item"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        action_data = {
            "action": "request_changes",
            "notes": "Please add a description",
        }

        response = client.post(
            f"/api/v1/admin/commons/submissions/{submission.id}/request-changes",
            json=action_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "needs_changes"

    def test_merge_submission(
        self, client, auth_headers, test_user, db_session
    ):
        """Test merging a submission into an existing entity."""
        # Create existing entity
        existing_entity = CommonsEntity(
            entity_type="item",
            data={"name": "Existing Item"},
            version=1,
            is_public=True,
            created_by=test_user.id,
        )
        db_session.add(existing_entity)
        db_session.commit()
        db_session.refresh(existing_entity)

        # Create submission to merge
        submission = CommonsSubmission(
            submitter_id=test_user.id,
            entity_type="item",
            entity_payload={"name": "Duplicate Item"},
            status="pending",
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        action_data = {
            "action": "merge",
            "action_payload": {"target_entity_id": str(existing_entity.id)},
            "notes": "Merged duplicate",
        }

        response = client.post(
            f"/api/v1/admin/commons/submissions/{submission.id}/merge",
            json=action_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "merged"


class TestPublicCommons:
    """Tests for public commons endpoints."""

    def test_list_public_items_no_auth(self, client, test_user, db_session):
        """Test listing public items without authentication."""
        # Create a public entity
        entity = CommonsEntity(
            entity_type="item",
            data={"name": "Public Item", "description": "A public item"},
            version=1,
            is_public=True,
            created_by=test_user.id,
        )
        db_session.add(entity)
        db_session.commit()

        response = client.get("/public/items")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert any(
            e["data"]["name"] == "Public Item" for e in data["entities"]
        )

    def test_get_public_item_no_auth(self, client, test_user, db_session):
        """Test getting a specific public item without authentication."""
        entity = CommonsEntity(
            entity_type="item",
            data={"name": "Public Item"},
            version=1,
            is_public=True,
            created_by=test_user.id,
        )
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)

        response = client.get(f"/public/items/{entity.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(entity.id)
        assert data["data"]["name"] == "Public Item"
        assert data["is_public"] is True

    def test_private_entity_not_visible(
        self, client, test_user, db_session
    ):
        """Test that private entities are not visible via public API."""
        entity = CommonsEntity(
            entity_type="item",
            data={"name": "Private Item"},
            version=1,
            is_public=False,
            created_by=test_user.id,
        )
        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)

        response = client.get(f"/public/items/{entity.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

