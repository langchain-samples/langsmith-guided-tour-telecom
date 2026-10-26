from utils.seeding import build_seed_plan, SINGLE_THREAD_PROMPTS, MULTITURN_CONVERSATIONS, CATEGORIES


def test_single_thread_prompts_are_five():
    assert len(SINGLE_THREAD_PROMPTS) == 5


def test_multiturn_has_multiple_turns():
    assert all(len(turns) >= 2 for turns in MULTITURN_CONVERSATIONS)


def test_categories_cover_expected_keys():
    assert set(CATEGORIES) == {"healthy", "hallucination_bait", "pii_leak", "broken_tool"}


def test_build_seed_plan_is_deterministic_and_sized():
    plan_a = build_seed_plan(n=30, seed=7)
    plan_b = build_seed_plan(n=30, seed=7)
    assert plan_a == plan_b           # deterministic
    assert len(plan_a) == 30
    cats = {cat for cat, _turns in plan_a}
    assert cats.issubset(set(CATEGORIES))
    assert all(isinstance(c, str) and isinstance(t, list) and t for c, t in plan_a)
