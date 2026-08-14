from framework.buddy_navigation_policy import BuddyNavigationPolicy, NavigationPreferences, NavigationState


def test_moving_driver_gets_navigation_priority():
    policy = BuddyNavigationPolicy(NavigationPreferences(avoid_highways=True, avoid_backroads=True))
    state = NavigationState(destination='home', moving=True)
    assert policy.route_constraints()['avoid_highways']
    assert policy.route_constraints()['avoid_backroads']
    assert policy.navigation_priority(state)[0] == 'turn_instructions'


def test_noncritical_request_is_queued_while_moving():
    state = NavigationState(moving=True)
    assert BuddyNavigationPolicy().handle_request(state, 'make a video') == 'queued_for_safe_interaction'
    assert state.queued_requests == ['make a video']


def test_critical_request_is_handled_now():
    state = NavigationState(moving=True)
    assert BuddyNavigationPolicy().handle_request(state, 'emergency', safety_critical=True) == 'handle_now'
