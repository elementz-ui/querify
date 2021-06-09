# Querify
This is a small module for parsing Elementz Table remote data options (such as filters, sorting, searching, offset, limit) and building SQL queries

## Install
`pip install elementz_querify`

## Usage

```python
import Querify from elementz_querify

querify = Querify(
	table_name="users",
	search_fields=('first','last','country'), # Searchable fields if we support searching 
	allowed_columns=['first','last','age','country','phone'], # Allowed filterable columns to prevent malicious injections
	custom_filters={  # Parsers for custom filters | By default a positive filter would be something like this "`age` = '[filter]'"
		'age':{
			'positive': {
				'Between 18 and 25': '(`age` > 18 AND `age` < 25)' 
			}
		}
	}
)

# items_sql - SQL query to get filtered items with the current limit & offset
# total_sql - SQL query to get the total count of filtered items

items_sql, total_sql = querify.build(
		0, # Offset
		10, # Limit
		searching="john", # Searching? 
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
	
print(items_sql)

```

The above code returns

```sql
SELECT * FROM `users` WHERE 
'john' IN (`first`, `last`, `country`) 
AND `first` = "josh" AND `first` = "paul" AND `first` = "john" AND `first` != "maria" 
AND (`age` > 18 AND `age` < 25) 
ORDER BY `age` DESC 
LIMIT 10 OFFSET 0
```