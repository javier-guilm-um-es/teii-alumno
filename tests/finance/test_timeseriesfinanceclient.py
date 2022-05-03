""" Unit tests for teii.finance.timeseries module """


import datetime as dt
import pytest

from pandas.testing import assert_series_equal

from teii.finance import FinanceClientInvalidData
from teii.finance import TimeSeriesFinanceClient
from teii.finance import FinanceClientInvalidAPIKey
from teii.finance import FinanceClientParamError


def test_constructor_success(api_key_str,
                             mocked_requests):
    TimeSeriesFinanceClient("IBM", api_key_str)


def test_constructor_failure_invalid_api_key():
    with pytest.raises(FinanceClientInvalidAPIKey):
        TimeSeriesFinanceClient("IBM")


def test_constructor_invalid_data(api_key_str, mocked_requests):
    with pytest.raises(FinanceClientInvalidData):
        TimeSeriesFinanceClient("NODATA", api_key_str)


def test_weekly_price_invalid_dates(api_key_str,
                                    mocked_requests):
    with pytest.raises(FinanceClientParamError):
        TimeSeriesFinanceClient("IBM", api_key_str).weekly_price(dt.date(2020, 10, 10), dt.date(2020, 10, 9))


def test_weekly_price_no_dates(api_key_str,
                               mocked_requests,
                               pandas_series_IBM_prices):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.weekly_price()

    assert ps.count() == 1162   # 2019-11-01 to 2022-02-11 (1162 business weeks)

    assert ps.count() == pandas_series_IBM_prices.count()

    assert_series_equal(ps, pandas_series_IBM_prices)


def test_weekly_price_dates(api_key_str,
                            mocked_requests,
                            pandas_series_IBM_prices_filtered):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.weekly_price(dt.date(year=2019, month=1, day=1),
                         dt.date(year=2021, month=12, day=31))

    assert ps.count() == 157    # 2019-01-01 to 2021-12-31 (157 business weeks)

    assert ps.count() == pandas_series_IBM_prices_filtered.count()

    assert_series_equal(ps, pandas_series_IBM_prices_filtered)


def test_weekly_volume_invalid_dates(api_key_str,
                                     mocked_requests):
    with pytest.raises(FinanceClientParamError):
        TimeSeriesFinanceClient("IBM", api_key_str).weekly_volume(dt.date(2020, 10, 10), dt.date(2020, 10, 9))


def test_weekly_volume_no_dates(api_key_str,
                                mocked_requests,
                                pandas_series_IBM_volumes):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.weekly_volume()

    assert ps.count() == 1162   # 2019-11-01 to 2022-02-11 (1162 business weeks)

    assert ps.count() == pandas_series_IBM_volumes.count()

    assert_series_equal(ps, pandas_series_IBM_volumes)


def test_weekly_volume_dates(api_key_str,
                             mocked_requests,
                             pandas_series_IBM_volumes_filtered):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.weekly_volume(dt.date(year=2019, month=1, day=1),
                          dt.date(year=2021, month=12, day=31))

    assert ps.count() == 157    # 2019-01-01 to 2021-12-31 (157 business weeks)

    assert ps.count() == pandas_series_IBM_volumes_filtered.count()

    assert_series_equal(ps, pandas_series_IBM_volumes_filtered)


def test_weekly_dividend_invalid_dates(api_key_str,
                                       mocked_requests):
    with pytest.raises(FinanceClientParamError):
        TimeSeriesFinanceClient("IBM", api_key_str).yearly_dividends(dt.date(2020, 1, 1), dt.date(2019, 1, 1))


def test_weekly_dividend_no_dates(api_key_str,
                                  mocked_requests,
                                  pandas_series_IBM_dividends):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.yearly_dividends()

    assert ps.count() == 24   # 2019-11-01 to 2022-02-11 (1162 business weeks)

    assert ps.count() == pandas_series_IBM_dividends.count()

    assert_series_equal(ps, pandas_series_IBM_dividends)


def test_weekly_divident_dates(api_key_str,
                               mocked_requests,
                               pandas_series_IBM_dividends_filtered):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.yearly_dividends(dt.date(2015, 1, 1), dt.date(2019, 1, 1))

    assert ps.count() == 5    # 2019-01-01 to 2021-12-31 (157 business weeks)

    assert ps.count() == pandas_series_IBM_dividends_filtered.count()

    assert_series_equal(ps, pandas_series_IBM_dividends_filtered)


def test_highest_weekly_variation_invalid_dates(api_key_str,
                                                mocked_requests):
    with pytest.raises(FinanceClientParamError):
        TimeSeriesFinanceClient("IBM", api_key_str).highest_weekly_variation(dt.date(2020, 10, 10), dt.date(2020, 10, 9))


def test_highest_weekly_variation_no_dates(api_key_str,
                                           mocked_requests):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.highest_weekly_variation()

    tupla_esperada = (dt.date(year=2020, month=3, day=13), 124.88, 100.81, 24.069999999999993)

    assert ps == tupla_esperada


def test_highest_weekly_variation_dates(api_key_str,
                                        mocked_requests):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.highest_weekly_variation(dt.date(year=2015, month=1, day=1),
                                     dt.date(year=2019, month=12, day=31))

    tupla_esperada = (dt.date(year=2018, month=4, day=20), 162.0, 144.51, 17.49000000000001)

    assert ps == tupla_esperada
