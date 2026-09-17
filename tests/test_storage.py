import io

import pytest

from app.storage.local import LocalStorage


def test_save_and_exists(tmp_path):
    storage = LocalStorage(tmp_path)

    content = b"Hello CSMBaseAPI"

    storage.save(
        "documents/test.txt",
        io.BytesIO(content),
    )

    assert storage.exists(
        "documents/test.txt"
    )

    with storage.open(
        "documents/test.txt"
    ) as stored_file:
        assert stored_file.read() == content


def test_open_reads_stored_file(tmp_path):
    storage = LocalStorage(tmp_path)

    content = b"Attachment content"

    storage.save(
        "documents/test.txt",
        io.BytesIO(content),
    )

    with storage.open("documents/test.txt") as file:
        assert file.read() == content


def test_delete_removes_stored_file(tmp_path):
    storage = LocalStorage(tmp_path)

    storage.save(
        "documents/test.txt",
        io.BytesIO(b"delete me"),
    )

    assert storage.exists(
        "documents/test.txt"
    )

    storage.delete(
        "documents/test.txt"
    )

    assert not storage.exists(
        "documents/test.txt"
    )


def test_save_creates_parent_directories(tmp_path):
    storage = LocalStorage(tmp_path)

    storage.save(
        "organizations/org/tasks/task/file.txt",
        io.BytesIO(b"nested"),
    )

    assert storage.exists(
        "organizations/org/tasks/task/file.txt"
    )


def test_storage_rejects_path_traversal(tmp_path):
    storage = LocalStorage(tmp_path)

    with pytest.raises(
        ValueError,
        match="outside the storage root",
    ):
        storage.save(
            "../../outside.txt",
            io.BytesIO(b"malicious"),
        )


def test_save_allows_file_at_max_size(tmp_path):
    storage = LocalStorage(tmp_path)

    content = b"x" * 10

    bytes_written = storage.save(
        "documents/exact-size.txt",
        io.BytesIO(content),
        max_size=10,
    )

    assert bytes_written == 10
    assert storage.exists(
        "documents/exact-size.txt"
    )

    with storage.open(
        "documents/exact-size.txt"
    ) as stored_file:
        assert stored_file.read() == content


def test_save_rejects_file_exceeding_max_size(tmp_path):
    storage = LocalStorage(tmp_path)

    content = b"x" * 11

    with pytest.raises(
        ValueError,
        match="File exceeds maximum allowed size",
    ):
        storage.save(
            "documents/too-large.txt",
            io.BytesIO(content),
            max_size=10,
        )

    assert not storage.exists(
        "documents/too-large.txt"
    )


def test_save_removes_partial_file_when_max_size_exceeded(
    tmp_path,
):
    storage = LocalStorage(tmp_path)

    content = b"x" * 2048

    with pytest.raises(
        ValueError,
        match="File exceeds maximum allowed size",
    ):
        storage.save(
            "documents/partial.txt",
            io.BytesIO(content),
            max_size=1024,
        )

    assert not storage.exists(
        "documents/partial.txt"
    )
