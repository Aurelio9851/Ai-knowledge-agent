from app.chunking import chunk_text


def test_chunk_text_short_text():
    text = "Hello world"

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert chunks == ["Hello world"]


def test_chunk_text_exact_chunk_size():
    text = "a" * 100

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert chunks == [text]


def test_chunk_text_creates_multiple_chunks():
    text = "a" * 250

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) == 3

    assert len(chunks[0]) == 100
    assert len(chunks[1]) == 100
    assert len(chunks[2]) == 90


def test_chunk_text_preserves_content():
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=2,
    )

    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "ijklmnopqr"
    assert chunks[2] == "qrstuvwxyz"


def test_chunk_text_has_correct_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=2,
    )

    assert chunks[0][-2:] == chunks[1][:2]
    assert chunks[1][-2:] == chunks[2][:2]


def test_chunk_text_empty_text():
    chunks = chunk_text(
        "",
        chunk_size=100,
        overlap=20,
    )

    assert chunks == []