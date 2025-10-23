import json
import os
from uuid import UUID

from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.models.task import Task, TaskStatus
from app.models.user import User
from app import tasks as task_module


def test_process_task_file_creates_result(monkeypatch, tmp_path):
    storage_root = tmp_path / "storage"
    uploads_dir = storage_root / "uploads"
    uploads_dir.mkdir(parents=True)

    sample_file = uploads_dir / "sample.txt"
    sample_file.write_text("sample content", encoding="utf-8")

    monkeypatch.setenv("STORAGE_ROOT", str(storage_root))

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session,
    )

    monkeypatch.setattr(task_module, "get_session_local", lambda: SessionLocal)

    with SessionLocal() as session:
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        task = Task(
            title="Test Task",
            description="Testing file processing",
            status=TaskStatus.PENDING,
            user_id=user.id,
            file_path=str(sample_file),
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = str(task.id)
        initial_updated_at = task.updated_at

    result = task_module.process_task_file(task_id, str(sample_file))

    assert result["status"] == "success"
    assert "result_path" in result

    with SessionLocal() as session:
        updated_task = session.get(Task, UUID(task_id))

        assert updated_task is not None
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.result_path is not None
        assert updated_task.completed_at is not None
        assert updated_task.updated_at is not None
        assert updated_task.updated_at >= updated_task.completed_at
        assert updated_task.updated_at > initial_updated_at
        assert updated_task.result_path.startswith(os.path.join(str(storage_root), "results"))
        assert os.path.exists(updated_task.result_path)

        with open(updated_task.result_path, "r", encoding="utf-8") as result_file:
            payload = json.load(result_file)

    assert payload["status"] == "success"
    assert payload["task_id"] == task_id
    assert payload["file_path"] == str(sample_file)
