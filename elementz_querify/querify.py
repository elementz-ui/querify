import MySQLdb


'''
	SQL Query Builder for Elementz Table
	https://github.com/elementz-ui/elementz

'''

class QuerifyException(Exception):
	pass

class Querify:

	def __init__(self, table_name=None, custom_filters=None, allowed_columns=None, search_fields=None):

		self.table_name = table_name if (
			table_name and isinstance(table_name,str)
		) else None
		
		self.allowed_columns = allowed_columns if (
			allowed_columns and isinstance(allowed_columns,list)
		) else None

		self.custom_filters =custom_filters if (
			custom_filters and isinstance(custom_filters,dict)
		) else None

		if isinstance(search_fields, tuple):
			search_fields = [*search_fields]
		
		self.search_fields = (
			', '.join(
				['`' + self.escape_string(sf) + '`' for sf in search_fields]
				)
		) if (
			search_fields and isinstance(search_fields,list)
		) else None

		pass

	
	def escape_string(self,s):
		return MySQLdb.escape_string(s).decode()


	def parse_filter(self, filter, col, filter_type):
		filters = []
		filter_types = {
			"positive": "=",
			"negative": "!=",
			#"like": "LIKE"
		}
		custom_filters = self.custom_filters

		filter_sign = filter_types[filter_type]

		for f in filter[col][filter_type]:
			if custom_filters and isinstance(custom_filters, dict) and (
				col in custom_filters and isinstance(custom_filters[col],dict) and filter_type in custom_filters[col]
				and f in custom_filters[col][filter_type]
			):
				filters.append(
					custom_filters[col][filter_type][f]
				)
				continue
			
			filters.append(
				"`{}` {} \"{}\"".format(self.escape_string(col),filter_sign, self.escape_string(f))	
			)

		return filters

	def build(self, offset, limit, search=None, filters=None, sort=None):
			conditions = []
			others = []

			if search and self.search_fields:
				search_fields = self.search_fields
				conditions.append(
					"'{}' IN ({})".format(self.escape_string(search), search_fields)
				)

			if filters and isinstance(filters, dict):
				for col in filters:
					if self.allowed_columns and col not in self.allowed_columns:
						raise QuerifyException("Column not allowed: %s" % col)

					if "positive" in filters[col] and isinstance(filters[col]["positive"], list):
						conditions.extend(
							self.parse_filter(filters, col, "positive")
						)

					if "negative" in filters[col] and isinstance(filters[col]["negative"], list):
						conditions.extend(
							self.parse_filter(filters, col, "negative")
						)

			if sort and isinstance(sort, dict) and "type" in sort and "column" in sort:
				sort_type = "DESC" if not sort["type"] else "ASC"
				sort_column = sort["column"]
				if self.allowed_columns and sort_column not in self.allowed_columns:
					raise QuerifyException("Column not allowed: %s" % sort_column)

				others.append(
					"ORDER BY `{}` {}".format(self.escape_string(sort_column), sort_type))
				)

			others.extend([
				"LIMIT {}".format(int(limit)),
				"OFFSET {}".format(int(offset))
			])

			sql = "{} {}".format(' AND '.join(conditions), ' '.join(others))

			if self.table_name:
				sql = "SELECT * FROM `{}`{}{}".format(self.table_name, (" WHERE " if len(conditions) else ""), sql)

			return sql

	
	
qm = Querify(
	table_name="users",
	search_fields=('first','last','country'),
	allowed_columns=['first','last','age','country','phone'],
	custom_filters=None
)
print(qm.build(0, 10, filters={
	'first':{
		'positive': ['lol', 'bro', 'wgat'],
		'negative': ['man']
	},
	'country':{
		'negative': ['london']
	}
	},
	search="ok"
))