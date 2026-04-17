from __future__ import annotations

import numpy as np
import pytest

from models import (
    CARBON_14_HALF_LIFE,
    CURRENT_YEAR,
    FLOOD_YEAR,
    FLOOD_YEAR_YEARS,
    ISOTOPE_SYSTEMS,
    LAMBDA,
    YEARS_SINCE_FLOOD,
    FloodAdjustedModel,
    LongAgeRadiometricSuite,
    RadiometricSystem,
    StandardModel,
    format_age,
)


class TestConstants:
    def test_c14_half_life(self):
        assert CARBON_14_HALF_LIFE == 5730

    def test_lambda_from_half_life(self):
        np.testing.assert_allclose(LAMBDA, np.log(2) / CARBON_14_HALF_LIFE, rtol=0, atol=1e-18)

    def test_years_since_flood(self):
        assert YEARS_SINCE_FLOOD == CURRENT_YEAR - FLOOD_YEAR

    @pytest.mark.parametrize("key", list(ISOTOPE_SYSTEMS.keys()))
    def test_isotope_lambda_consistency(self, key):
        info = ISOTOPE_SYSTEMS[key]
        np.testing.assert_allclose(info["lambda"], np.log(2) / info["half_life"])


class TestStandardModel:
    def setup_method(self):
        self.m = StandardModel()

    def test_name(self):
        assert self.m.name == "Standard Scientific Model"

    def test_calculate_age_one_half_life(self):
        np.testing.assert_allclose(
            self.m.calculate_age(0.5), CARBON_14_HALF_LIFE, rtol=1e-12
        )

    def test_calculate_age_ratio_zero_returns_inf(self):
        assert self.m.calculate_age(0) == float("inf")

    def test_calculate_age_ratio_negative_returns_inf(self):
        assert self.m.calculate_age(-0.1) == float("inf")

    def test_predict_ratio_one_half_life(self):
        np.testing.assert_allclose(
            self.m.predict_ratio(CARBON_14_HALF_LIFE), 0.5, rtol=1e-12
        )

    def test_predict_ratio_zero_age(self):
        assert self.m.predict_ratio(0) == 1.0

    @pytest.mark.parametrize("age", [100, 1000, 5730, 10000, 50000])
    def test_calculate_and_predict_are_inverses(self, age):
        ratio = self.m.predict_ratio(age)
        np.testing.assert_allclose(self.m.calculate_age(ratio), age, rtol=1e-10)


class TestFloodAdjustedModel:
    def setup_method(self):
        self.m = FloodAdjustedModel()

    def test_name_and_defaults(self):
        assert self.m.name == "Flood-Adjusted Model"
        assert self.m.pre_flood_c14_ratio == 0.30
        assert self.m.water_vapor_canopy == 0.70
        assert self.m.magnetic_field_factor == 2.0
        assert self.m.flood_temperature_c == 100.0
        assert self.m.water_depth_feet == 90000.0
        assert self.m.post_flood_equilibrium_years == 2000
        assert self.m.ocean_reservoir_factor == 0.60
        assert self.m.burial_depth_m == 0.0
        assert self.m.volcanic_activity_factor == 1.5

    def test_cosmic_ray_shielding_formula(self):
        expected = (1.0 / self.m.magnetic_field_factor) * (1.0 - self.m.water_vapor_canopy)
        np.testing.assert_allclose(self.m._cosmic_ray_shielding(), expected)

    def test_temperature_pressure_factor_positive(self):
        assert self.m._temperature_pressure_factor() > 0

    def test_temperature_pressure_factor_increases_with_burial(self):
        base = self.m._temperature_pressure_factor()
        self.m.burial_depth_m = 100.0
        deeper = self.m._temperature_pressure_factor()
        assert deeper > base

    def test_post_flood_buildup_at_zero_returns_preflood_ratio(self):
        assert self.m._post_flood_c14_buildup(0) == self.m.pre_flood_c14_ratio

    def test_post_flood_buildup_negative_returns_preflood_ratio(self):
        assert self.m._post_flood_c14_buildup(-5) == self.m.pre_flood_c14_ratio

    def test_post_flood_buildup_increases_over_time(self):
        early = self.m._post_flood_c14_buildup(100)
        late = self.m._post_flood_c14_buildup(3000)
        assert late > early

    def test_post_flood_buildup_clamped_to_one(self):
        self.m.volcanic_activity_factor = 1.0
        self.m.ocean_reservoir_factor = 10.0
        assert self.m._post_flood_c14_buildup(10000) <= 1.0

    def test_effective_initial_preflood_organism(self):
        preflood_true_age = YEARS_SINCE_FLOOD + 100
        expected = self.m.pre_flood_c14_ratio * self.m._cosmic_ray_shielding()
        np.testing.assert_allclose(
            self.m.effective_initial_c14(preflood_true_age), expected
        )

    def test_effective_initial_during_flood(self):
        flood_age = YEARS_SINCE_FLOOD - 0.5
        expected = self.m.pre_flood_c14_ratio * 0.5
        np.testing.assert_allclose(self.m.effective_initial_c14(flood_age), expected)

    def test_effective_initial_postflood_in_range(self):
        ratio = self.m.effective_initial_c14(1000)
        assert 0.0 < ratio < 1.0

    def test_predict_measured_ratio_post_flood_positive(self):
        ratio = self.m.predict_measured_ratio(1000)
        assert ratio > 0.0

    def test_predict_measured_ratio_near_flood_applies_tp_factor(self):
        near_flood_true_age = YEARS_SINCE_FLOOD - 0.5
        ratio = self.m.predict_measured_ratio(near_flood_true_age)
        assert ratio >= 1e-15

    def test_predict_measured_ratio_has_numerical_floor(self):
        assert self.m.predict_measured_ratio(1e9) >= 1e-15

    def test_standard_date_overestimates_post_flood(self):
        true_age = 1000
        standard_date = self.m.standard_date_for_true_age(true_age)
        assert standard_date > true_age

    def test_standard_date_measured_ratio_zero_branch(self, monkeypatch):
        monkeypatch.setattr(self.m, "predict_measured_ratio", lambda age: 0.0)
        assert self.m.standard_date_for_true_age(100) == float("inf")

    def test_generate_comparison_data_default_max(self):
        data = self.m.generate_comparison_data()
        assert len(data["true_ages"]) == 200
        assert data["true_ages"][0] == 100
        assert data["true_ages"][-1] == CURRENT_YEAR
        for key in ("standard_dates", "initial_ratios", "measured_ratios"):
            assert len(data[key]) == 200

    def test_generate_comparison_data_explicit_bounds(self):
        data = self.m.generate_comparison_data(max_true_age=5000, steps=50)
        assert len(data["true_ages"]) == 50
        assert data["true_ages"][-1] == 5000


class TestFormatAge:
    @pytest.mark.parametrize(
        "years,expected_substring",
        [
            (4.5e9, "billion years"),
            (1.5e6, "million years"),
            (5000, "thousand years"),
            (500, "500 years"),
        ],
    )
    def test_format_branches(self, years, expected_substring):
        assert expected_substring in format_age(years)


class TestRadiometricSystem:
    @pytest.mark.parametrize("key", list(ISOTOPE_SYSTEMS.keys()))
    def test_zero_accel_zero_initial_recovers_elapsed_epoch_time(self, key):
        system = RadiometricSystem(
            system_key=key,
            initial_daughter_ratio=0.0,
            creation_acceleration_log10=0.0,
            flood_acceleration_log10=0.0,
        )
        expected_elapsed = FLOOD_YEAR + FLOOD_YEAR_YEARS + YEARS_SINCE_FLOOD
        np.testing.assert_allclose(system.apparent_age(), expected_elapsed, rtol=1e-6)

    @pytest.mark.parametrize("key", list(ISOTOPE_SYSTEMS.keys()))
    def test_mass_conservation_across_epochs(self, key):
        initial_daughter = 0.10
        system = RadiometricSystem(
            system_key=key,
            initial_daughter_ratio=initial_daughter,
            creation_acceleration_log10=11.0,
            flood_acceleration_log10=3.0,
        )
        expected_total = 1.0 + initial_daughter
        for epoch in system.get_epoch_breakdown():
            np.testing.assert_allclose(
                epoch["P_after"] + epoch["D_after"], expected_total, rtol=1e-12
            )

    def test_acceleration_log_to_linear(self):
        system = RadiometricSystem(
            "U-Pb",
            creation_acceleration_log10=11.0,
            flood_acceleration_log10=3.0,
        )
        np.testing.assert_allclose(system.creation_acceleration, 1e11)
        np.testing.assert_allclose(system.flood_acceleration, 1e3)

    def test_system_metadata_populated(self):
        system = RadiometricSystem("U-Pb")
        assert system.key == "U-Pb"
        assert system.parent_name == "U-238"
        assert system.daughter_name == "Pb-206"
        assert system.half_life == 4.468e9
        assert system.description == "Uranium-Lead"

    def test_daughter_parent_ratio_exceeds_initial(self):
        initial = 0.50
        system = RadiometricSystem(
            "U-Pb",
            initial_daughter_ratio=initial,
            creation_acceleration_log10=11.0,
            flood_acceleration_log10=0.0,
        )
        assert system.daughter_parent_ratio() > initial

    def test_epoch_breakdown_structure(self):
        epochs = RadiometricSystem("K-Ar").get_epoch_breakdown()
        assert len(epochs) == 4
        assert "Creation Week" in epochs[0]["name"]
        assert "Pre-Flood" in epochs[1]["name"]
        assert "Flood Year" in epochs[2]["name"]
        assert "Post-Flood" in epochs[3]["name"]
        for epoch in epochs:
            assert set(epoch.keys()) == {
                "name", "duration", "acceleration", "P_after", "D_after", "consumed",
            }

    def test_extreme_acceleration_zeros_parent_apparent_age(self):
        system = RadiometricSystem(
            "U-Pb",
            creation_acceleration_log10=30.0,
            flood_acceleration_log10=0.0,
        )
        assert system.apparent_age() == float("inf")

    def test_extreme_acceleration_zeros_parent_daughter_parent_ratio(self):
        system = RadiometricSystem(
            "U-Pb",
            creation_acceleration_log10=30.0,
            flood_acceleration_log10=0.0,
        )
        assert system.daughter_parent_ratio() == float("inf")


class TestLongAgeRadiometricSuite:
    def test_defaults_populate_all_systems(self):
        suite = LongAgeRadiometricSuite()
        assert set(suite.systems.keys()) == set(ISOTOPE_SYSTEMS.keys())
        for system in suite.systems.values():
            assert system.creation_acceleration_log10 == LongAgeRadiometricSuite.DEFAULT_CREATION_ACCEL_LOG10
            assert system.flood_acceleration_log10 == LongAgeRadiometricSuite.DEFAULT_FLOOD_ACCEL_LOG10

    def test_defaults_use_default_initial_daughters(self):
        suite = LongAgeRadiometricSuite()
        for key, default in LongAgeRadiometricSuite.DEFAULT_INITIAL_DAUGHTERS.items():
            assert suite.systems[key].initial_daughter_ratio == default

    def test_explicit_parameters_applied(self):
        suite = LongAgeRadiometricSuite(
            creation_accel_log10=10.0,
            flood_accel_log10=2.0,
            initial_daughters={"U-Pb": 0.1, "K-Ar": 0.2, "Rb-Sr": 0.3},
        )
        assert suite.systems["U-Pb"].initial_daughter_ratio == 0.1
        assert suite.systems["K-Ar"].initial_daughter_ratio == 0.2
        assert suite.systems["Rb-Sr"].initial_daughter_ratio == 0.3
        for system in suite.systems.values():
            assert system.creation_acceleration_log10 == 10.0
            assert system.flood_acceleration_log10 == 2.0

    def test_partial_initial_daughters_defaults_missing_to_zero(self):
        suite = LongAgeRadiometricSuite(initial_daughters={"U-Pb": 0.9})
        assert suite.systems["U-Pb"].initial_daughter_ratio == 0.9
        assert suite.systems["K-Ar"].initial_daughter_ratio == 0.0
        assert suite.systems["Rb-Sr"].initial_daughter_ratio == 0.0

    def test_apparent_ages_returns_all_systems(self):
        ages = LongAgeRadiometricSuite().apparent_ages()
        assert set(ages.keys()) == set(ISOTOPE_SYSTEMS.keys())
        for age in ages.values():
            assert age > 0

    def test_summary_table_shape_and_keys(self):
        rows = LongAgeRadiometricSuite().summary_table()
        assert len(rows) == len(ISOTOPE_SYSTEMS)
        for row in rows:
            assert set(row.keys()) == {
                "System", "Half-Life", "D/P Ratio", "Apparent Age", "True Age",
            }
