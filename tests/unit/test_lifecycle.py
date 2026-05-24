"""
DreamCo OS — Unit Tests: Lifecycle State Machine
"""

import pytest
from python_bots.core.lifecycle import BotState, assert_transition, IllegalStateTransitionError


class TestLifecycle:
    def test_idle_to_running_allowed(self):
        assert_transition(BotState.IDLE, BotState.RUNNING)

    def test_running_to_idle_allowed(self):
        assert_transition(BotState.RUNNING, BotState.IDLE)

    def test_running_to_quarantined_allowed(self):
        assert_transition(BotState.RUNNING, BotState.QUARANTINED)

    def test_quarantined_to_idle_allowed(self):
        assert_transition(BotState.QUARANTINED, BotState.IDLE)

    def test_stopped_to_idle_allowed(self):
        assert_transition(BotState.STOPPED, BotState.IDLE)

    def test_idle_to_quarantined_blocked(self):
        with pytest.raises(IllegalStateTransitionError):
            assert_transition(BotState.IDLE, BotState.QUARANTINED)

    def test_quarantined_to_running_blocked(self):
        with pytest.raises(IllegalStateTransitionError):
            assert_transition(BotState.QUARANTINED, BotState.RUNNING)

    def test_stopped_to_running_blocked(self):
        with pytest.raises(IllegalStateTransitionError):
            assert_transition(BotState.STOPPED, BotState.RUNNING)

    def test_all_states_have_valid_transitions(self):
        for state in BotState:
            # Should not raise — every state has a defined transition map
            assert state in BotState
