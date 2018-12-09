import logging

import numpy as np
import pytest

from climate_indices import compute, indices

# ----------------------------------------------------------------------------------------------------------------------
# disable logging messages
logging.disable(logging.CRITICAL)


"""
Tests for `indices.py`.
"""


# ---------------------------------------------------------------------------------------
@pytest.mark.usefixtures(
    "precips_mm_monthly",
    "pet_thornthwaite_mm",
    "awc_inches",
    "data_year_start_monthly",
    "calibration_year_start_monthly",
    "calibration_year_end_monthly",
)
def test_pdsi(
    precips_mm_monthly,
    pet_thornthwaite_mm,
    awc_inches,
    data_year_start_monthly,
    calibration_year_start_monthly,
    calibration_year_end_monthly,
):

    # the indices.pdsi() function is a wrapper for palmer.pdsi(), so we'll
    # just confirm that this function can be called without raising an error and
    # the palmer.pdsi() function itself is being tested within test_palmer.py
    indices.pdsi(
        precips_mm_monthly,
        pet_thornthwaite_mm,
        awc_inches,
        data_year_start_monthly,
        calibration_year_start_monthly,
        calibration_year_end_monthly,
    )


# ---------------------------------------------------------------------------------------
@pytest.mark.usefixtures(
    "precips_mm_monthly",
    "pet_thornthwaite_mm",
    "awc_inches",
    "data_year_start_monthly",
    "calibration_year_start_monthly",
    "calibration_year_end_monthly",
)
def test_scpdsi(
    precips_mm_monthly,
    pet_thornthwaite_mm,
    awc_inches,
    data_year_start_monthly,
    calibration_year_start_monthly,
    calibration_year_end_monthly,
):

    # the indices.scpdsi() function is a wrapper for palmer.scpdsi(), so we'll
    # just confirm that this function can be called without raising an error and
    # the palmer.scpdsi() function itself is being tested within test_palmer.py
    indices.scpdsi(
        precips_mm_monthly,
        pet_thornthwaite_mm,
        awc_inches,
        data_year_start_monthly,
        calibration_year_start_monthly,
        calibration_year_end_monthly,
    )


# ----------------------------------------------------------------------------------------
@pytest.mark.usefixtures("temps_celsius", "latitude_degrees", "data_year_start_monthly")
def test_pet(temps_celsius, latitude_degrees, data_year_start_monthly):

    # confirm that an input array of all NaNs for temperature results in the same array returned
    all_nan_temps = np.full(temps_celsius.shape, np.NaN)
    computed_pet = indices.pet(all_nan_temps, latitude_degrees, data_year_start_monthly)
    np.testing.assert_equal(
        computed_pet,
        all_nan_temps,
        "All-NaN input array does not result in the expected all-NaN result",
    )

    # confirm that a masked input array of all NaNs for temperature results in the same masked array returned
    masked_all_nan_temps = np.ma.array(all_nan_temps)
    computed_pet = indices.pet(
        masked_all_nan_temps, latitude_degrees, data_year_start_monthly
    )
    np.testing.assert_equal(
        computed_pet,
        masked_all_nan_temps,
        "All-NaN masked input array does not result in the expected all-NaN masked result",
    )

    # confirm that a missing/None latitude value raises an error
    np.testing.assert_raises(
        ValueError, indices.pet, temps_celsius, None, data_year_start_monthly
    )

    # confirm that a missing/None latitude value raises an error
    np.testing.assert_raises(
        ValueError, indices.pet, temps_celsius, np.NaN, data_year_start_monthly
    )

    # confirm that an invalid latitude value raises an error
    pytest.raises(
        ValueError,
        indices.pet,
        temps_celsius,
        91.0,  # latitude > 90 is invalid
        data_year_start_monthly,
    )

    # confirm that an invalid latitude value raises an error
    np.testing.assert_raises(
        ValueError,
        indices.pet,
        temps_celsius,
        -91.0,  # latitude < -90 is invalid
        data_year_start_monthly,
    )

    # compute PET from the monthly temperatures, latitude, and initial years -- if this runs without
    # error then this test passes, as the underlying method(s) being used to compute PET will be tested
    # in the relevant test_compute.py or test_eto.py codes
    indices.pet(temps_celsius, latitude_degrees, data_year_start_monthly)

    # compute PET from the monthly temperatures, latitude (as an array), and initial years -- if this runs without
    # error then this test passes, as the underlying method(s) being used to compute PET will be tested
    # in the relevant test_compute.py or test_eto.py codes
    indices.pet(temps_celsius, np.array([latitude_degrees]), data_year_start_monthly)


# ----------------------------------------------------------------------------------------
@pytest.mark.usefixtures(
    "precips_mm_monthly",
    "data_year_start_monthly",
    "calibration_year_start_monthly",
    "calibration_year_end_monthly",
    "pnp_6month",
)
def test_pnp(
    precips_mm_monthly,
    data_year_start_monthly,
    calibration_year_start_monthly,
    calibration_year_end_monthly,
    pnp_6month,
):

    # confirm that an input array of all NaNs for precipitation results in the same array returned
    all_nan_precips = np.full(precips_mm_monthly.shape, np.NaN)
    computed_pnp = indices.percentage_of_normal(
        all_nan_precips,
        1,
        data_year_start_monthly,
        calibration_year_start_monthly,
        calibration_year_end_monthly,
        compute.Periodicity.monthly,
    )
    np.testing.assert_allclose(
        computed_pnp.flatten(),
        all_nan_precips.flatten(),
        equal_nan=True,
        err_msg="All-NaN input array does not result in the expected all-NaN result",
    )

    # compute PNP from the daily precipitation array
    computed_pnp_6month = indices.percentage_of_normal(
        precips_mm_monthly.flatten(),
        6,
        data_year_start_monthly,
        calibration_year_start_monthly,
        calibration_year_end_monthly,
        compute.Periodicity.monthly,
    )

    # confirm PNP is being computed as expected
    np.testing.assert_allclose(
        pnp_6month.flatten(),
        computed_pnp_6month.flatten(),
        atol=0.01,
        equal_nan=True,
        err_msg="PNP values not computed as expected",
    )

    # confirm we can compute PNP from the daily values without raising an error
    indices.percentage_of_normal(
        precips_mm_daily.flatten(),
        30,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        compute.Periodicity.daily,
    )

    # invalid periodicity argument should raise an Error
    np.testing.assert_raises(
        ValueError,
        indices.percentage_of_normal,
        precips_mm_daily.flatten(),
        30,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        "unsupported_value",
    )

    # invalid scale argument should raise an Error
    np.testing.assert_raises(
        ValueError,
        indices.percentage_of_normal,
        precips_mm_daily.flatten(),
        -3,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        compute.Periodicity.daily,
    )
    np.testing.assert_raises(
        ValueError,
        indices.percentage_of_normal,
        precips_mm_daily.flatten(),
        None,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        compute.Periodicity.daily,
    )


# ----------------------------------------------------------------------------------------
def test_spi(self):

    # confirm that an input array of all NaNs for precipitation results in the same array returned
    all_nans = np.full(precips_mm_monthly.shape, np.NaN)
    computed_spi = indices.spi(
        all_nans,
        1,
        indices.Distribution.gamma,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
        compute.Periodicity.monthly,
    )
    np.testing.assert_allclose(
        computed_spi,
        all_nans.flatten(),
        equal_nan=True,
        err_msg="SPI/Gamma not handling all-NaN arrays as expected",
    )

    # confirm SPI/gamma is being computed as expected
    computed_spi = indices.spi(
        precips_mm_monthly,
        1,
        indices.Distribution.gamma,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
        compute.Periodicity.monthly,
    )
    np.testing.assert_allclose(
        computed_spi,
        spi_1_month_gamma,
        atol=0.001,
        err_msg="SPI/Gamma values for 1-month scale not computed as expected",
    )

    # confirm SPI/gamma is being computed as expected
    computed_spi = indices.spi(
        precips_mm_monthly.flatten(),
        6,
        indices.Distribution.gamma,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
        compute.Periodicity.monthly,
    )

    # confirm SPI/gamma is being computed as expected
    np.testing.assert_allclose(
        computed_spi,
        spi_6_month_gamma,
        atol=0.001,
        err_msg="SPI/Gamma values for 6-month scale not computed as expected",
    )

    # confirm we can also call the function with daily data, if this completes without error then test passes
    indices.spi(
        precips_mm_daily,
        30,
        indices.Distribution.gamma,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        compute.Periodicity.daily,
    )

    # invalid periodicity argument should raise a ValueError
    np.testing.assert_raises(
        ValueError,
        indices.spi,
        precips_mm_monthly.flatten(),
        6,
        indices.Distribution.gamma,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
        "unsupported_value",
    )

    # invalid distribution argument should raise a ValueError
    np.testing.assert_raises(
        ValueError,
        indices.spi,
        precips_mm_monthly.flatten(),
        6,
        None,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
        compute.Periodicity.monthly,
    )

    # input array argument that's neither 1-D nor 2-D should raise a ValueError
    np.testing.assert_raises(
        ValueError,
        indices.spi,
        np.array(np.zeros((4, 4, 8))),
        6,
        indices.Distribution.gamma,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
        compute.Periodicity.daily,
    )

    # compute SPI/Pearson at 60-day scale, just make sure it completes without error
    # TODO compare against expected results
    indices.spi(
        precips_mm_daily.flatten(),
        60,
        indices.Distribution.pearson,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        compute.Periodicity.daily,
    )

    # confirm SPI/Pearson is being computed as expected
    computed_spi = indices.spi(
        precips_mm_monthly.flatten(),
        6,
        indices.Distribution.pearson,
        data_year_start_monthly,
        calibration_year_start_monthly,
        calibration_year_end_monthly,
        compute.Periodicity.monthly,
    )
    np.testing.assert_allclose(
        computed_spi,
        spi_6_month_pearson3,
        atol=0.01,
        err_msg="SPI/Pearson values for 6-month scale not computed as expected",
    )

    # confirm we can compute from daily values without raising an error
    indices.spi(
        precips_mm_daily.flatten(),
        60,
        indices.Distribution.pearson,
        data_year_start_daily,
        calibration_year_start_daily,
        calibration_year_end_daily,
        compute.Periodicity.daily,
    )

    # invalid periodicity argument should raise a ValueError
    np.testing.assert_raises(
        ValueError,
        indices.spi,
        precips_mm_monthly.flatten(),
        6,
        indices.Distribution.pearson,
        data_year_start_monthly,
        calibration_year_start_monthly,
        calibration_year_end_monthly,
        "unsupported_value",
    )


# ----------------------------------------------------------------------------------------
def test_spei(self):

    # confirm that an input array of all NaNs for precipitation results in the same array returned
    all_nans = np.full(precips_mm_monthly.shape, np.NaN)
    computed_spei = indices.spei(
        all_nans,
        all_nans,
        1,
        indices.Distribution.gamma,
        compute.Periodicity.monthly,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
    )
    np.testing.assert_allclose(
        computed_spei,
        all_nans,
        equal_nan=True,
        err_msg="SPEI/Gamma not handling all-NaN arrays as expected",
    )

    # compute SPEI/gamma at 6-month scale
    computed_spei = indices.spei(
        precips_mm_monthly,
        pet_mm,
        6,
        indices.Distribution.gamma,
        compute.Periodicity.monthly,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
    )

    # confirm SPEI/gamma is being computed as expected
    np.testing.assert_allclose(
        computed_spei,
        spei_6_month_gamma,
        atol=0.01,
        err_msg="SPEI/Gamma values for 6-month scale not computed as expected",
    )

    # compute SPEI/Pearson at 6-month scale
    computed_spei = indices.spei(
        precips_mm_monthly,
        pet_mm,
        6,
        indices.Distribution.pearson,
        compute.Periodicity.monthly,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
    )

    # confirm SPEI/Pearson is being computed as expected
    np.testing.assert_allclose(
        computed_spei,
        spei_6_month_pearson3,
        atol=0.01,
        err_msg="SPEI/Pearson values for 6-month scale not computed as expected",
    )

    # invalid periodicity argument should raise a ValueError
    np.testing.assert_raises(
        ValueError,
        indices.spei,
        precips_mm_monthly,
        pet_mm,
        6,
        indices.Distribution.pearson,
        "unsupported_value",
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
    )

    # having both precipitation and PET input array arguments with incongruent dimensions should raise a ValueError
    np.testing.assert_raises(
        ValueError,
        indices.spei,
        precips_mm_monthly,
        np.array((200, 200), dtype=float),
        6,
        indices.Distribution.pearson,
        compute.Periodicity.monthly,
        data_year_start_monthly,
        data_year_start_monthly,
        data_year_end_monthly,
    )
