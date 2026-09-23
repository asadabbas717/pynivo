from pynivo.core.execution import OutputBuffer


def test_output_buffer_keeps_newest_text_with_semantic_type() -> None:
    buffer = OutputBuffer(maximum_characters=10)

    assert not buffer.append("12345")
    assert buffer.append("abcdefgh", error=True)

    chunks = buffer.chunks()
    assert "".join(chunk.text for chunk in chunks) == "45abcdefgh"
    assert chunks[-1].error


def test_output_buffer_clear_and_validation() -> None:
    buffer = OutputBuffer(5)
    buffer.append("hello")
    buffer.clear()

    assert buffer.chunks() == ()
