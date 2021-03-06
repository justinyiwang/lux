from .context import lux
import pytest
import pandas as pd
import numpy as np
from lux.utils import date_utils
from lux.executor.PandasExecutor import PandasExecutor

def test_dateformatter():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	timestamp = np.datetime64('2019-08-26')
	ldf.maintain_metadata()
	assert(date_utils.date_formatter(timestamp,ldf) == '2019')

	ldf["Year"][0] = np.datetime64('1970-03-01') # make month non unique

	assert (date_utils.date_formatter(timestamp, ldf) == '2019-8')


	ldf["Year"][0] = np.datetime64('1970-03-03') # make day non unique

	assert (date_utils.date_formatter(timestamp, ldf) == '2019-8-26')

def test_period_selection():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')

	ldf["Year"] = pd.DatetimeIndex(ldf["Year"]).to_period(freq='A')

	ldf.set_intent([lux.Clause(attribute = ["Horsepower", "Weight", "Acceleration"]), lux.Clause(attribute ="Year")])

	PandasExecutor.execute(ldf.current_vis, ldf)

	assert all([type(vlist.data) == lux.core.frame.LuxDataFrame for vlist in ldf.current_vis])
	assert all(ldf.current_vis[2].data.columns == ["Year", 'Acceleration'])

def test_period_filter():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')

	ldf["Year"] = pd.DatetimeIndex(ldf["Year"]).to_period(freq='A')

	ldf.set_intent([lux.Clause(attribute ="Acceleration"), lux.Clause(attribute ="Horsepower")])

	PandasExecutor.execute(ldf.current_vis, ldf)
	ldf._repr_html_()

	assert isinstance(ldf.recommendation['Filter'][2]._inferred_intent[2].value, pd.Period)

def test_period_to_altair():
	chart = None
	df = pd.read_csv("lux/data/car.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')

	df["Year"] = pd.DatetimeIndex(df["Year"]).to_period(freq='A')

	df.set_intent([lux.Clause(attribute ="Acceleration"), lux.Clause(attribute ="Horsepower")])

	PandasExecutor.execute(df.current_vis, df)
	df._repr_html_()

	exported_code = df.recommendation['Filter'][2].to_Altair()
	
	assert 'Year = 1971' in exported_code

def test_refresh_inplace():
	df = pd.DataFrame({'date': ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01'], 'value': [10.5,15.2,20.3,25.2]})
	with pytest.warns(UserWarning,match="Lux detects that the attribute 'date' may be temporal."):
		df._repr_html_()
	assert df.data_type_lookup["date"]=="temporal"

	from lux.vis.Vis import Vis
	vis = Vis(["date","value"],df)

	df['date'] = pd.to_datetime(df['date'],format="%Y-%m-%d")
	df.maintain_metadata()
	assert df.data_type['temporal'][0] == 'date'

	vis.refresh_source(df)
	assert vis.mark == "line"
	assert vis.get_attr_by_channel("x")[0].attribute == "date"
	assert vis.get_attr_by_channel("y")[0].attribute == "value"