import math

from app.core.utils import scr_normalize


def test_r2_animal_adverse_event_zero_count() -> None:
    assert scr_normalize.r2_animal_adverse_event(0) == 0.0


def test_r2_animal_adverse_event_hand_calculated() -> None:
    # 25 * log10(100) = 25 * 2 = 50
    assert scr_normalize.r2_animal_adverse_event(99) == 50.0


def test_r2_animal_adverse_event_caps_at_100() -> None:
    assert scr_normalize.r2_animal_adverse_event(999_999) == 100.0


def test_o1_literature_scarcity_zero_count_is_max_scarcity() -> None:
    assert scr_normalize.o1_literature_scarcity(0) == 100.0


def test_o1_literature_scarcity_hand_calculated() -> None:
    # 100 - 30 * log10(10) = 100 - 30 = 70
    assert scr_normalize.o1_literature_scarcity(9) == 70.0


def test_o1_literature_scarcity_floors_at_zero() -> None:
    assert scr_normalize.o1_literature_scarcity(10_000_000) == 0.0


def test_o1_literature_scarcity_matches_manual_formula() -> None:
    count = 42
    expected = max(0.0, 100.0 - 30.0 * math.log10(count + 1))
    assert scr_normalize.o1_literature_scarcity(count) == expected


def test_o2_clinical_absence_zero_trials_is_max_absence() -> None:
    assert scr_normalize.o2_clinical_absence(0) == 100.0


def test_o2_clinical_absence_hand_calculated() -> None:
    # 100 - 40 * log10(3) = 100 - 40 * 0.4771... = 80.9144...
    assert scr_normalize.o2_clinical_absence(2) == max(0.0, 100.0 - 40.0 * math.log10(3))


def test_o2_clinical_absence_floors_at_zero() -> None:
    assert scr_normalize.o2_clinical_absence(10_000_000) == 0.0


def test_r1_clinical_warning_no_warnings() -> None:
    assert scr_normalize.r1_clinical_warning([]) == 0.0


def test_r1_clinical_warning_black_box_only() -> None:
    warnings = [{"warningType": "Black Box Warning"}]
    assert scr_normalize.r1_clinical_warning(warnings) == 60.0


def test_r1_clinical_warning_withdrawn_outranks_black_box() -> None:
    warnings = [{"warningType": "Black Box Warning"}, {"warningType": "Withdrawn"}]
    assert scr_normalize.r1_clinical_warning(warnings) == 100.0


def test_r3_voluntary_withdrawal_no_record() -> None:
    assert scr_normalize.r3_voluntary_withdrawal([]) == 0.0


def test_r3_voluntary_withdrawal_has_record() -> None:
    assert scr_normalize.r3_voluntary_withdrawal([{"application_number": "005-414"}]) == 100.0
