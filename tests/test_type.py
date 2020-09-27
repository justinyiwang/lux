from .context import lux
import pytest
import pandas as pd

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
