from bots.stripe_builder_bot import StripeBuilderBot


def test_secret_profile_packet_uses_aliases_without_values():
    bot = StripeBuilderBot()

    packet = bot.build_secret_profile_packet("new account")

    assert packet["status"] == "secret_profile_ready"
    assert packet["secret_values_included"] is False
    assert packet["default_secret_aliases"]["secret_key"] == ["STRIPE_SECRET_KEY", "STRIPE_API_KEY"]
    assert packet["profile_secret_names"]["secret_key"] == "STRIPE_SECRET_KEY_NEW_ACCOUNT"
    assert "add_or_rotate_stripe_secret" in packet["approval_required_before"]


def test_secret_rotation_plan_is_approval_gated():
    bot = StripeBuilderBot()

    plan = bot.build_secret_rotation_plan("old stripe", "new stripe")

    assert plan["status"] == "stripe_secret_rotation_plan_ready"
    assert plan["live_action"] is False
    assert plan["secret_values_included"] is False
    assert plan["old_profile"]["secret_key"] == "STRIPE_SECRET_KEY_OLD_STRIPE"
    assert plan["new_profile"]["secret_key"] == "STRIPE_SECRET_KEY_NEW_STRIPE"
    assert "switch_active_stripe_profile" in plan["approval_required_before"]
