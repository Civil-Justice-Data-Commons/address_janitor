# Address Janitor
A basic python address cleaner, developed for use with Civil Justice Data Commons court records addresses.

Written by James Carey for the Georgetown CJDC (@carey-james).

## Functionality
Takes an address and attempts to match its zip code, county, and city name to a set of databases. If matches are found, returns a 'corrected' address that matches the databases.

This is done through finding a modified Damerau-Levenshtein distance between the entered address and the entries in a database and then returning the closest match. This calculation is modified to weigh in favor of letter substitutions that could easily be achieved by typos on a standard QWERTY keyboard.

Initial version is only set up to work with data from Arizona.

## Use
### Example:
`address_janitor.clean('1035 W Main St #46, Mea AZ 8500E')`
returns:
`'1035 W Main St #46, Mesa AZ 85003'`
### Methods:
```python
address_janitor.clean(address, county='', state='', d_weight='', i_weight='', s_weight='', t_weight='')
```
#### Inputs: 
* **address:** *string*, a street address including city name and zip to be cleaned (if one is missing, will be ignored), including state in postal code form is ideal
* **county:** *string*, *optional*, the county the address is in, in title case
* **state:** *string*, *optional*, the state the address is in, in 2 character uppercase postal form
* **d_weight:** *int*, *optional*, weight for deletion in the modified Damerau-Levenshtein distance, default is 1
* **i_weight:** *int*, *optional*, weight for insertion in the modified Damerau-Levenshtein distance, default is 1
* **s_weight:** *int*, *optional*, weight for substitution in the modified Damerau-Levenshtein distance, default is 1
* **t_weight:** *int*, *optional*, weight for transposition in the modified Damerau-Levenshtein distance, default is 1
#### Outputs:
* *string*, a cleaned version of the original address, with the city and/or zip code replaced with cleaned versions


## Sources
City data is derived from www.openstreetmap.org. The data is made available under ODbL.