from .context import lux
import pytest
import pandas as pd
import numpy as np
from typing import List
from dataclasses import dataclass

# Suite of test that checks if data_type inferred correctly by Lux
def test_check_cars():
	df = pd.read_csv("lux/data/car.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y') 
	df.maintain_metadata()
	assert df.data_type_lookup["Name"] == "nominal"
	assert df.data_type_lookup['MilesPerGal'] == 'quantitative'
	assert df.data_type_lookup['Cylinders'] == 'nominal'
	assert df.data_type_lookup['Displacement'] == 'quantitative'
	assert df.data_type_lookup['Horsepower'] == 'quantitative'
	assert df.data_type_lookup['Weight'] == 'quantitative'
	assert df.data_type_lookup['Acceleration'] == 'quantitative'
	assert df.data_type_lookup['Year'] == 'temporal'
	assert df.data_type_lookup['Origin'] == 'nominal'

def test_check_id():
	df = pd.read_csv('https://github.com/lux-org/lux-datasets/blob/master/data/instacart_sample.csv?raw=true')
	df._repr_html_()
	assert len(df.data_type["id"])==3
	assert "<code>order_id</code> is not visualized since it resembles an ID field." in df._message.to_html()
	assert "<code>product_id</code> is not visualized since it resembles an ID field." in df._message.to_html()
	assert "<code>user_id</code> is not visualized since it resembles an ID field." in df._message.to_html()

def test_check_id_no_regex():
	#rename all column names and rerun data
	@dataclass
	class TestCase:
		name: str
		ids: List[str] #a set of column 0-indices that should recognizes as id
	testcases = [
		TestCase(name='spotify', ids=['id']),
		TestCase(name='airbnb_nyc', ids=['id']),
		TestCase(name='churn', ids=['customerID']),
		TestCase(name='employee', ids=['EmployeeNumber'])
	]

	for case in testcases:
		url = 'https://github.com/lux-org/lux-datasets/blob/master/data/' + case.name + '.csv?raw=true'
		df = pd.read_csv(url)

		#rename col to str(0-index of col) to avoid reliance on regex
		new_cols = [str(i) for i in np.arange(len(df.columns))]
		col_map = dict(zip(new_cols, df.columns))
		df.columns = new_cols
		df.expire_metadata()
		df.maintain_metadata()
		for col in new_cols:
			col_type = df.data_type_lookup[col]
			if col_map[col] in case.ids:
				assert col_type == 'id', 'col %s in set %s not recognized as id' % (col_map[col], case.name)
			else:
				assert col_type != 'id', 'col %s in set %s misidentified as id' % (col_map[col], case.name)

