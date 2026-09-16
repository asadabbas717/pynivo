from pynivo.learning import ExampleLibrary


def test_bundled_examples_are_valid_and_unique() -> None:
    examples = ExampleLibrary().load()

    assert len(examples) >= 4
    assert len({example.identifier for example in examples}) == len(examples)
    assert all(example.title and example.category and example.code for example in examples)
    assert all(compile(example.code, f"<{example.identifier}>", "exec") for example in examples)
