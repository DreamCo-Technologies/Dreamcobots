import pytest

from buddy_os.intelligence.reasoning_memory import ReasoningCase, ReasoningCaseLibrary


def test_case_library_prefers_tag_overlap_then_verified_cases():
    library = ReasoningCaseLibrary()
    library.add(ReasoningCase("a", "diagnosis", frozenset({"causal", "systems"}), "sig-a", ("causal",), verified=True))
    library.add(ReasoningCase("b", "diagnosis", frozenset({"systems"}), "sig-b", ("abductive",)))
    library.add(ReasoningCase("c", "planning", frozenset({"causal"}), "sig-c", ("simulation",)))
    results = library.retrieve("diagnosis", ["causal", "systems"], limit=2)
    assert [case.case_id for case in results] == ["a", "b"]
    assert library.verified_cases()[0].case_id == "a"


def test_case_library_rejects_duplicates_and_bad_limit():
    library = ReasoningCaseLibrary()
    case = ReasoningCase("x", "logic", frozenset(), "sig", ("deductive",))
    library.add(case)
    with pytest.raises(ValueError):
        library.add(case)
    with pytest.raises(ValueError):
        library.retrieve("logic", limit=0)
