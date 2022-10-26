###
# Address Janitor for the Georgetown Civil Justice Data Commons designed by James Carey (@carey-james).
###

import csv
import usaddress

import numpy as np
import pandas as pd

ZIP_FILEPATH = 'zip_table.csv'
CITY_FILEPATH = 'city_table.csv'

IMPLEMENTED_STATES = ['AZ']

# Threshold for distance algo
THRESHOLD = 3

# D-L Distance weights
DELETE_WEIGHT = 1
INSERT_WEIGHT = 1
SUB_START_WEIGHT = 1
TRANSPO_WEIGHT = 1

# Set up the keyboard for use in the typo section of the distance finding algo.
KEYBOARD = {
	'`':(0,0),'~':(0,0),'1':(1,0),'!':(1,0),'2':(2,0),'@':(2,0),'3':(3,0),'#':(3,0),'4':(4,0),'$':(4,0),'5':(5,0),'%':(5,0),'6':(6,0),'^':(6,0),'7':(7,0),'&':(7,0),'8':(8,0),'*':(8,0),'9':(9,0),'(':(9,0),'0':(10,0),')':(10,0),'-':(11,0),'_':(11,0),'=':(12,0),'+':(12,0),
	'Q':(1,1),'W':(2,1),'E':(3,1),'R':(4,1),'T':(5,1),'Y':(6,1),'U':(7,1),'I':(8,1),'O':(9,1),'P':(10,1),'[':(11,1),'{':(11,1),']':(12,1),'}':(12,1),'\\':(13,1),'|':(13,1),
	'A':(1,2),'S':(2,2),'D':(3,2),'F':(4,2),'G':(5,2),'H':(6,2),'J':(7,2),'K':(8,2),'L':(9,2),';':(10,2),':':(10,2),'\'':(11,2),'"':(11,2),
	'Z':(1,3),'X':(2,3),'C':(3,3),'V':(4,3),'B':(5,3),'N':(6,3),'M':(7,3),',':(8,3),'<':(9,3),'.':(10,3),'>':(10,3),'/':(11,3),'?':(11,3)
}

def file_loader(filepath):
	df = pd.read_csv(filepath, encoding='utf8')
	return df
		
# Find the Damerau-Levenshtein distance for the address and table string, modified to increase accuracy for keyboard typos.
def mod_d_l_dist(address_string, target_string):
	
	two_d_array = {}
	len_add = len(address_string)
	len_targ = len(target_string)

	for i in range(-1,len_add+1):
		two_d_array[(i,-1)] = i+1
	for j in range(-1,len_targ+1):
		two_d_array[(-1,j)] = j+1

	for i in range(len_add):
		for j in range(len_targ):
			if address_string[i] == target_string[j]:
				cost = 0
				keyboard_dist = 0
			else:
				cost = 1
				# find the distance between two keys on the keyboard, then divided by 2 (to ID a 'close' key on a 0-1 scale, where 2 keys away is the closet 'close'), and if that is greater than 1, set to 1.
				try:
					keyboard_dist = min((((abs(KEYBOARD[address_string[i].upper()][0] - KEYBOARD[target_string[j].upper()][0]) + abs(KEYBOARD[address_string[i].upper()][1] - KEYBOARD[target_string[j].upper()][1]))) / 2), 1)
				except:
					keyboard_dist = 1
			two_d_array[(i,j)] = min(
						   two_d_array[(i-1,j)] + DELETE_WEIGHT, # deletion
						   two_d_array[(i,j-1)] + INSERT_WEIGHT, # insertion
						   two_d_array[(i-1,j-1)] + (cost * keyboard_dist * SUB_START_WEIGHT), # substitution
						  )
			if i and j and address_string[i]==target_string[j-1] and address_string[i-1] == target_string[j]:
				two_d_array[(i,j)] = min (two_d_array[(i,j)], two_d_array[i-2,j-2] + (cost * TRANSPO_WEIGHT)) # transposition

	return two_d_array[len_add-1,len_targ-1]

# Take an address string and a corisponding target string list, find which string on that list the address string best matches, returns that matching target and the mod Damerau-Levenshtein distance of that string
def best_mod_d_l_dist(address_string, target_string_list):
	best_match = ['',9999]
	for targ in target_string_list:
		mod_d_l = mod_d_l_dist(str(address_string), str(targ))
		if mod_d_l < best_match[1]:
			best_match = [targ, mod_d_l]
	return best_match

def clean(address, county='', state='', d_weight='', i_weight='', s_weight='', t_weight=''):

	new_address = address

	# If we were given a county, make sure we were given a state
	if (county != '') and (state == ''):
		print('County was given but not state. State must be provided if county is.')
		return


	# Set up weights
	if d_weight != '': DELETE_WEIGHT = d_weight
	if i_weight != '': INSERT_WEIGHT = i_weight
	if s_weight != '': SUB_START_WEIGHT = s_weight
	if t_weight != '': TRANSPO_WEIGHT = t_weight
	
	# Chop up the address with usaddress
	chopped_address = usaddress.parse(address)
	
	# Stick that chopped up address into a dict
	address_dict = {}
	for piece in chopped_address:
		if piece[1] in address_dict:
			address_dict[piece[1]] = f'{address_dict[piece[1]]} {piece[0]}'
		else:
			address_dict[piece[1]] = piece[0]

	if 'StateName' in address_dict:
		if state == '':
			state = address_dict['StateName']
		elif state != address_dict['StateName']:
			print(f'Given state {state} does not match address state {address_dict["StateName"]}, skip out of state address.')
			return

	# Check if the state has been implemented
	if (state != '') and not state in IMPLEMENTED_STATES:
		print(f'{state} is not an Implemented state.')
		return

	# Open up the tables
	zip_df = file_loader(ZIP_FILEPATH)
	city_df = file_loader(CITY_FILEPATH)

	# Check that the county given is inside the state given
	if (county != '') and (state not in (zip_df.loc[zip_df['county'] == county, 'state'].values[0])):
		print('Could not find the given county in the given state. Ensure county is in titlecase and state is 2 letter code.')
		return


	# Attempt to find a clean city name
	if 'PlaceName' in address_dict:
		if county != '':
			city_list = city_df.query(f'(county == "{county}") & (state == "{state}")')['city'].tolist()
		elif state != '':
			city_list = city_df.query(f'(state == "{state}")')['city'].tolist()
		else:
			city_list = city_df['city'].tolist()
		city_match = best_mod_d_l_dist(address_dict['PlaceName'], city_list)
		print(city_match)
		if city_match[1] < THRESHOLD:
			new_address = new_address.replace(address_dict['PlaceName'],city_match[0])

	# Attempt to find a clean Zip Code
	if 'ZipCode' in address_dict:
		if county != '':
			zip_list = zip_df.query(f'(county == "{county}") & (state == "{state}")')['zip'].tolist()
		elif state != '':
			zip_list = zip_df.query(f'(state == "{state}")')['zip'].tolist()
		else:
			zip_list = zip_df['zip'].tolist()
		zip_match = best_mod_d_l_dist(address_dict['ZipCode'], zip_list)
		print(zip_match)
		if zip_match[1] < THRESHOLD:
			new_address = new_address.replace(str(address_dict['ZipCode']),str(zip_match[0]))

	return new_address
