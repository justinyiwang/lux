def convert_to_list(x):
	'''
	"a" --> ["a"]
	["a","b"] --> ["a","b"]
	'''
	if type(x) != list:
		return [x]
	else:
		return x

def pandas_to_lux(df):
	from lux.core.frame import LuxDataFrame
	values = df.values.tolist()
	ldf = LuxDataFrame(values, columns = df.columns)
	return(ldf)

def get_attrs_specs(intent):
	if (intent is None): return []
	spec_obj = list(filter(lambda x: x.value=="", intent))
	return spec_obj

def get_filter_specs(intent):
	if (intent is None): return []
	spec_obj = list(filter(lambda x: x.value!="", intent))
	return spec_obj

def check_import_lux_widget():
	import pkgutil
	if (pkgutil.find_loader("luxWidget") is None):
		raise Exception("luxWidget is not installed. Run `npm i lux-widget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget")

def get_agg_title(clause):
	if (clause.aggregation is None):
		return f'{clause.attribute}'
	elif (clause.attribute=="Record"):
		return f'Number of Records'
	else:
		return f'{clause._aggregation_name.capitalize()} of {clause.attribute}'

def check_if_id_like(df,attribute):
	import re
	from pandas.api.types import is_numeric_dtype
	import numpy as np
	# Strong signals
	high_cardinality = df.cardinality[attribute] > 500 # so that aggregated reset_index fields don't get misclassified
	attribute_contain_id = re.search(r'id',attribute) is not None
	almost_all_vals_unique = df.cardinality[attribute] >= 0.98 * len(df)

	#weak signals - should prompt user for further action, but do not automatically remove
	#numerical-only default to false, as can only be evaluated for numerical data
	vals_equally_spaced = False #check if interval between attribute is mostly equal
	weak_correlation = False #check if attribute is very weakly correlated with all other cols
	if is_numeric_dtype(df[attribute][0]):
		diffs = np.diff(df[attribute].sort_values(), axis=0)
		values, counts = np.unique(diffs, return_counts=True)
		if max(counts) >= 0.95 * len(diffs):
			vals_equally_spaced = True

		corr = df.corr().abs().drop(attribute, axis=1)
		attr_idx = list(corr.index).index(attribute)
		max_corr = df.iloc[[attr_idx]].max(axis=1)
		if max_corr < .1:
			weak_correlation = True

	# TODO: Could probably add some type of entropy measure (since the binned id fields are usually very even)
	return high_cardinality and (attribute_contain_id or almost_all_vals_unique)