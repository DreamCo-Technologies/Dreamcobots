from framework.agent_routing_engine import AgentProfile, AgentRouter, CapabilityEvidence, TaskStep


def ev(cap, score):
    return CapabilityEvidence(capability=cap, quality=score, speed=score, efficiency=score, reliability=score, safety=score, samples=10)


def test_router_prefers_evidence_and_can_use_multiple_agents():
    router=AgentRouter([
        AgentProfile('python', frozenset({'python'}), (ev('python', .95),)),
        AgentProfile('security', frozenset({'security'}), (ev('security', .90),)),
        AgentProfile('weak', frozenset({'python'}), (ev('python', .20),)),
    ])
    plan=router.plan([TaskStep('build', frozenset({'python','security'}), independent_verification=True)])
    assert plan.assignments['build'] == ['python','security']
    assert not plan.unresolved


def test_router_reports_uncovered_capabilities():
    router=AgentRouter([AgentProfile('python', frozenset({'python'}), (ev('python', .9),))])
    plan=router.plan([TaskStep('x', frozenset({'python','ios'}))])
    assert 'ios' in plan.unresolved['x']
