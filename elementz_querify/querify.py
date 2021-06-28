import MySQLdb


'''
	SQL Query Builder for Elementz Table
	https://github.com/elementz-ui/elementz

'''

class QuerifyException(Exception):
	pass

class Querify:

	def __init__(self, 
			table_name=None,  
			filterable_columns=None, 
			searchable_columns=None, 
			custom_filters=None, 
			custom_search=None, 
			search_ci=False, 
			column_escape='`', 
			table_escape=''
		):

		self.table_name = table_name if (
			table_name and isinstance(table_name,str)
		) else None
		
		self.filterable_columns = filterable_columns if (
			filterable_columns and isinstance(filterable_columns,list)
		) else None

		self.searchable_columns = searchable_columns if (
			searchable_columns and isinstance(searchable_columns,list)
		) else None

		self.custom_filters = custom_filters if (
			custom_filters and isinstance(custom_filters,dict)
		) else None

		self.custom_search = custom_search if (
			custom_search and (isinstance(custom_search, dict) or callable(custom_search))
		) else None
		
		self.search_ci = search_ci
		self.column_escape = column_escape
		self.table_escape = table_escape

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
					"(%s)" % custom_filters[col][filter_type][f]
				)
				continue
			
			filters.append(
				"{}{}{} {} '{}'".format(self.column_escape, self.escape_string(col), self.column_escape, filter_sign, self.escape_string(f))	
			)

		return filters

	def build(self, offset, limit, search=None, filters=None, sort=None):
			conditions = []
			others = []

			if filters and isinstance(filters, dict):
				for col in filters:
					if not filters[col]:
						continue
					if self.filterable_columns and col not in self.filterable_columns:
						raise QuerifyException("Column not allowed: %s" % col)

					if "positive" in filters[col] and isinstance(filters[col]["positive"], list):
						conditions.extend(
							self.parse_filter(filters, col, "positive")
						)

					if "negative" in filters[col] and isinstance(filters[col]["negative"], list):
						conditions.extend(
							self.parse_filter(filters, col, "negative")
						)
			
			if search and (self.searchable_columns or callable(self.custom_search)):
				if callable(self.custom_search):
					conditions.append(
						"({})".format(self.custom_search(search))
					)
				else:
					search_fields = self.searchable_columns
					search_conditions = []

					for sf in search_fields:
						search_ci = ' COLLATE UTF8_GENERAL_CI ' if self.search_ci else '' # Case Insesitive Search
						search_conditions.append(
							"{}{}{}{} LIKE '%{}%'".format(self.column_escape, self.escape_string(sf), self.column_escape, search_ci, self.escape_string(search))
						)

					conditions.append(
						"({})".format(' OR '.join(search_conditions))
					)

			if sort and isinstance(sort, dict) and "type" in sort and "column" in sort and sort["column"]:
				sort_type = "DESC" if not sort["type"] else "ASC"
				sort_column = sort["column"]
				if self.filterable_columns and sort_column not in self.filterable_columns:
					raise QuerifyException("Column not allowed: %s" % sort_column)

				others.append(
					"ORDER BY {}{}{} {}".format(self.column_escape, self.escape_string(sort_column), self.column_escape,  sort_type)
				)

			others.extend([
				"LIMIT {}".format(int(limit)),
				"OFFSET {}".format(int(offset))
			])

			conditions_sql = ' AND '.join(conditions)
			others_sql = ' '.join(others)
			sql = "{} {}".format(conditions_sql, others_sql)
			total_sql = None

			if self.table_name:
				hasConditions =  (" WHERE " if len(conditions) else "")
				sql = "SELECT * FROM {}{}{}{}{}".format(self.table_escape, self.table_name, self.table_escape, hasConditions, sql)
				total_sql = "SELECT count(*) as total FROM {}{}{}{}{}".format(self.table_escape, self.table_name, self.table_escape, hasConditions, conditions_sql)

			return [sql, total_sql]

	
''' Test
querify = Querify(
	table_name="users",
	searchable_columns=('first','last','country'), # Searchable fields if we support searching 
	filterable_columns=['first','last','age','country','phone'], # Allowed filterable columns to prevent malicious injections
	custom_filters={  # Parsers for custom filters | By default a positive filter would be something like this "`age` = '[filter]'"
		'age':{
			'positive': {
				'Between 18 and 25': '(`age` > 18 AND `age` < 25)' 
			}
		}
	}
)

print(
	querify.build(
		0, # Offset
		10, # Limit
		search="john", # Searching? 
		filters={ # Filters
			'first':{
				'positive': ['josh', 'paul', 'john'],
				'negative': ['maria']
			},
			'age':{
				'positive': ['Between 18 and 25']
			}
		},
		sort={ # Sorting
			'type': False,
			'column': 'age'
		}
	)
)

'''