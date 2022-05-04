""" Time Series Finance Client classes """


import datetime as dt
import logging
import pandas as pd

from typing import Optional, Union

from teii.finance import FinanceClientParamError
from teii.finance import FinanceClientInvalidData
from teii.finance import FinanceClient


class TimeSeriesFinanceClient(FinanceClient):
    """ Wrapper around the AlphaVantage API for Time Series Weekly Adjusted.

        Source:
            https://www.alphavantage.co/documentation/ (TIME_SERIES_WEEKLY_ADJUSTED)
    """

    _data_field2name_type = {
            "1. open":                  ("open",     "float"),
            "2. high":                  ("high",     "float"),
            "3. low":                   ("low",      "float"),
            "4. close":                 ("close",    "float"),
            "5. adjusted close":        ("aclose",   "float"),
            "6. volume":                ("volume",   "int"),
            "7. dividend amount":       ("dividend", "float")
        }

    def __init__(self, ticker: str,
                 api_key: Optional[str] = None,
                 logging_level: Union[int, str] = logging.WARNING) -> None:
        """ TimeSeriesFinanceClient constructor. """

        super().__init__(ticker, api_key, logging_level)

        self._build_data_frame()
        self._logger.info("Objeto de tipo TimeSeriesFinanceClient creado")

    def _build_data_frame(self) -> None:
        """ Build Panda's DataFrame and format data. """

        # TODO
        #   Comprueba que no se produce ningún error y genera excepción
        #   'FinanceClientInvalidData' en caso de error
        try:
            # Build Panda's data frame
            data_frame = pd.DataFrame.from_dict(self._json_data, orient='index', dtype=float)

            # Rename data fields
            data_frame = data_frame.rename(columns={key: name_type[0]
                                                    for key, name_type in self._data_field2name_type.items()})

            # Set data field types
            data_frame = data_frame.astype(dtype={name_type[0]: name_type[1]
                                                  for key, name_type in self._data_field2name_type.items()})

            # Set index type
            data_frame.index = data_frame.index.astype("datetime64[ns]")

            # Sort data
            self._data_frame = data_frame.sort_index(ascending=True)

        except Exception as e:
            raise FinanceClientInvalidData("Datos inválidos para la construcción del dataframe") from e
        else:
            self._logger.info("Data frame construido")

    def _build_base_query_url_params(self) -> str:
        """ Return base query URL parameters.

        Parameters are dependent on the query type:
            https://www.alphavantage.co/documentation/
        URL format:
            https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=TICKER&outputsize=full&apikey=API_KEY&data_type=json
        """

        self._logger.info("Obteniendo parámetros para base query URL solicitada.")
        return f"function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={self._ticker}&outputsize=full&apikey={self._api_key}"

    @classmethod
    def _build_query_data_key(cls) -> str:
        """ Return data query key. """

        return "Weekly Adjusted Time Series"

    def _validate_query_data(self) -> None:
        """ Validate query data. """

        try:
            assert self._json_metadata["2. Symbol"] == self._ticker
        except Exception as e:
            raise FinanceClientInvalidData("Metadata field '2. Symbol' not found") from e
        else:
            self._logger.info(f"Metadata key '2. Symbol' = '{self._ticker}' found")

    def weekly_price(self,
                     from_date: Optional[dt.date] = None,
                     to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly close price from 'from_date' to 'to_date'.

        Parameters
        ----------
        from_date : datetime.date
            parámetro que indica desde qué fecha de inicio queremos buscar (opcional)
        to_date : datetime.date
            parámetro que indica hasta qué fecha final queremos buscar (opcional)

        Returns
        -------
        series : pandas.Series
            devuelve una serie con los precios semanales entre las fechas indicadas (o todas en caso de no indicar fechas)

        Raises
        ------
        FinanceClientParamError
            Si la fecha from_date es posterior a to_date
        """

        assert self._data_frame is not None

        series = self._data_frame['aclose']

        # FIXME: type hint error
        if from_date is not None and to_date is not None:
            try:
                assert from_date <= to_date

            except Exception as e:
                raise FinanceClientParamError("Error en los parámetros introducidos") from e

            else:
                self._logger.info(f"Precio semanal filtrado desde {from_date} hasta {to_date}.")
                series = series.loc[from_date:to_date]  # type: ignore
        else:
            self._logger.info("Precios obtenidos de todos los registros semanales.")

        return series

    def weekly_volume(self,
                      from_date: Optional[dt.date] = None,
                      to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly volume from 'from_date' to 'to_date'.

        Parameters
        ----------
        from_date : datetime.date
            parámetro que indica desde qué fecha de inicio queremos buscar (opcional)
        to_date : datetime.date
            parámetro que indica hasta qué fecha final queremos buscar (opcional)

        Returns
        -------
        series : pandas.Series
            devuelve una serie con los volúmenes semanales entre las fechas indicadas (o todas en caso de no indicar fechas)

        Raises
        ------
        FinanceClientParamError
            Si la fecha from_date es posterior a to_date
        """

        assert self._data_frame is not None

        series = self._data_frame['volume']

        if from_date is not None and to_date is not None:
            try:
                assert from_date <= to_date

            except Exception as e:
                raise FinanceClientParamError("Error en los parámetros introducidos") from e
            else:
                self._logger.info(f"Volumen semanal filtrado desde {from_date} hasta {to_date}.")
                series = series.loc[from_date:to_date]  # type: ignore
        else:
            self._logger.info("Volúmenes obtenidos de todos los registros semanales.")

        return series

    def yearly_dividends(self,
                         from_year: Optional[dt.date] = None,
                         to_year: Optional[dt.date] = None) -> pd.Series:
        """ Return yearly dividend from 'from_year' to 'to_year'.

        Parameters
        ----------
        from_year : datetime.date
            parámetro que indica desde qué fecha (se cogerá el año) de inicio queremos buscar (opcional)
        to_year : datetime.date
            parámetro que indica hasta qué fecha (se cogerá el año) final queremos buscar (opcional)

        Returns
        -------
        series : pandas.Series
            devuelve una serie con los dividendos anuales entre los años indicadas (o todos en caso de no indicar rango)

        Raises
        ------
        FinanceClientParamError
            Si la fecha from_year es posterior a to_year
        """

        assert self._data_frame is not None

        series = self._data_frame.groupby(pd.Grouper(freq='YS'))['dividend'].sum()

        if from_year is not None and to_year is not None:
            try:
                assert from_year.year <= to_year.year

            except Exception as e:
                raise FinanceClientParamError("Error en los parámetros introducidos") from e
            else:
                self._logger.info(f"Dividendos anuales filtrados desde {from_year} hasta {to_year}.")
                series = series.loc[from_year:to_year]  # type: ignore
        else:
            self._logger.info("Dividendos obtenidos de todos los años.")

        series.index = pd.to_datetime(series.index, format='%Y-%m-%d').strftime('%Y')
        series.index = pd.to_datetime(series.index)

        return series

    def highest_weekly_variation(self,
                                 from_date: Optional[dt.date] = None,
                                 to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly highest variation from 'from_date' to 'to_date'.

        Parameters
        ----------
        from_date : datetime.date
            parámetro que indica desde qué fecha de inicio queremos buscar (opcional)
        to_date : datetime.date
            parámetro que indica hasta qué fecha final queremos buscar (opcional)

        Returns
        -------
        series : pandas.Series
            devuelve una tupla con la información de la semana con mayor variación entre el valor high y low, entre las fechas indicadas (o todas en caso de no indicar fechas)

        Raises
        ------
        FinanceClientParamError
            Si la fecha from_date es posterior a to_date
        """

        assert self._data_frame is not None

        self._data_frame['high-low'] = self._data_frame['high'] - self._data_frame['low']

        series = self._data_frame[['high', 'low', 'high-low']]

        if from_date is not None and to_date is not None:
            try:
                assert from_date <= to_date

            except Exception as e:
                raise FinanceClientParamError("Error en los parámetros introducidos") from e
            else:
                self._logger.info(f"Variación máxima semanal filtrada desde {from_date} hasta {to_date}.")
                series = series.loc[from_date:to_date]  # type: ignore
        else:
            self._logger.info("Variación máxima obtenida de todos los registros semanales.")

        fila = series.loc[series['high-low'] == series['high-low'].max(), :]

        fecha_timestamp = pd.Timestamp(fila.index[0])

        fecha = dt.date(year=fecha_timestamp.year, month=fecha_timestamp.month, day=fecha_timestamp.day)

        tupla = (fecha, fila.iloc[0, 0], fila.iloc[0, 1], fila.iloc[0, 2])

        return tupla
