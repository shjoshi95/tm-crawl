# Written by Shreyes H. Joshi, Princeton University


import urllib2  			   # used to request info from url's
from lxml import etree as ET   # xml parsing module
import re 					   # regular expression module
import time					   # time tracking module
from storage_secured_ver4 import insert
import httplib

ns_tmk = 'http://www.wipo.int/standards/XMLSchema/Trademark/1'  # namespace 1
ns_com = 'http://www.wipo.int/standards/XMLSchema/Common/1'		# namespace 2
ns_tmk2 = '{http://www.wipo.int/standards/XMLSchema/Trademark/1}' # {ns_tmk2}
ns_com2 = '{http://www.wipo.int/standards/XMLSchema/Common/1}'	 # {ns_com2}

# the url segments below form the link to the xml file source online
url_part1 = 'https://tsdrapi.uspto.gov/ts/cd/casestatus/sn'	# url segment 1
url_part2 = '/info.xml'										# url segment 2

# these paths are file paths to certain nodes in the xml file parsed from uspto
path_start_standard = '/tmk:Transaction/tmk:TrademarkTransactionBody \
			  		   /tmk:TransactionContentBag/tmk:TransactionData \
					   /tmk:TrademarkBag/tmk:Trademark' 
path_start_mark = path_start_standard + '/tmk:MarkEventBag' 
path_start_gs_bag = path_start_standard + '/tmk:GoodsServicesBag \
			  							   /tmk:GoodsServices \
			  							   /tmk:GoodsServicesClassificationBag'
path_start_national_cor = path_start_standard + '/tmk:NationalCorrespondent'
path_start_record_attorney = path_start_standard + '/tmk:RecordAttorney' 
path_start_applicant = path_start_standard + '/tmk:ApplicantBag'
path_start_nat_trade = path_start_standard + '/tmk:NationalTrademarkInformation'

# each list of elements contains the tags for desired data from the xml tree
single_elements = ['RegistrationOfficeCode', 'IPOfficeCode', \
				   'ApplicationNumberText', 'RegistrationNumber', \
				   'ApplicationDate', 'RegistrationDate', 'FilingPlace', \
				   'MarkCurrentStatusDate', 'MarkCategory', \
				   'MarkFeatureCategory', 'FirstUsedDate', \
				   'FirstUsedCommerceDate', 'PublicationIdentifier', \
				   'PublicationDate', 'ClassNumber', \
				   'GoodsServicesDescriptionText', 'MarkVerbalElementText', \
				   'MarkSignificantVerbalElementText', \
				   'MarkStandardCharacterIndicator', 'ImageFileName', \
				   'MarkImageColourClaimedText',  \
				   'MarkImageColourPartClaimedText', 'ImageColourIndicator', \
				   'MarkSound', 'BasisForeignApplicationIndicator', \
				   'BasisForeignRegistrationIndicator', 'BasisUseIndicator', \
				   'BasisIntentToUseIndicator', 'NoBasisIndicator', \
				   'NationalStatusExternalDescriptionText', \
				   'NationalStatusCategory', 'NationalStatusCode']
mark_elements = ['MarkEventCategory', 'MarkEventCode', \
				 'MarkEventDescriptionText', 'MarkEventEntryNumber', \
				 'MarkEventAdditionalText', 'MarkEventDate']
gs_elements = ['ClassificationKindCode', 'ClassNumber', 'NationalClassNumber']
national_cor_elements = ['PersonFullName', 'OrganizationStandardName', \
						 'AddressLineText', 'AddressLineText2', 'CityName', \
						 'GeographicRegionName', 'CountryCode', \
						 'PostalCode', 'PhoneNumber', 'FaxNumber', \
						 'EmailAddressText']
record_attorney_elements = ['PersonFullName', 'CommentText']
applicant_elements = ['LegalEntityName', 'NationalLegalEntityCode', \
					  'IncorporationCountryCode', 'IncorporationState', \
					  'CommentText', 'OrganizationStandardName', \
					  'EntityName', 'EntityNameCategory', 'AddressLineText', \
					  'AddressLineText2', 'CityName', 'GeographicRegionName',\
					  'CountryCode', 'PostalCode']
nat_trade_elements = ['RegisterCategory','AmendedPrincipalRegisterIndicator', \
					  'AmendedSupplementalRegisterIndicator', \
					  'MarkCurrentStatusExternalDescriptionText']
stops = 0	# tracks number of server disconnections

# receives the span of serial numbers to process and parses data from xmls
# sends this data to the be stored in a database specified in settings.py
# no return type
def traverse(span):
	for trademark in span:
		tree = make_tree(trademark) # retrieves the xml file as element tree 
		
		# each 'data' element contains data collected from a certain node 
		#  of the given xml tree
		# note: the first variable here, data, contains general elements from 
		#  the root node of the tree
		data = load_data(tree, path_start_standard)
		mark_data = load_rep(tree, path_start_mark, mark_elements)
		gs_bag_data = load_rep(tree, path_start_gs_bag, gs_elements)
		national_cor_data = load_data(tree, path_start_national_cor)
		record_attorney_data = load_data(tree, path_start_record_attorney)
		applicant_data = load_rep(tree, path_start_applicant, \
								  applicant_elements)
		nat_trade_data = load_data(tree, path_start_nat_trade)

		to_insert = [data, single_elements, mark_data, mark_elements, \
					 gs_bag_data, gs_elements, national_cor_data, \
					 national_cor_elements, record_attorney_data, \
					 record_attorney_elements, applicant_data, \
					 applicant_elements, nat_trade_data, nat_trade_elements]
		 # all the data dictionaries and their corresponding tag lists
		 # are passed to insert(), which stores these fields in postgres
		insert(to_insert)

# writes the to_write string to the file output in utf-8
# no return type (void)
def write(to_write, output):
	try:
		output.write(to_write)
	except UnicodeEncodeError:
		to_write = to_write.encode('utf-8')
		output.write(to_write)


#  This method constructs a unique url based on the serial provided. 
#  The tree then parses all the information from the url. If the 
#  server unplugs the program user, then the method waits 1.5 seconds 
#  before trying again, and will continue to run until the server 
#  provides all the information. The variable stops will keep track of 
#  every time the server unplugs the user.
# returns xml tree object
def make_tree(serial):

	url = url_part1 + str(serial) + url_part2 # create unique url with serial # 
	serial_stops = 0
	while True:
		try:
			source = urllib2.Request(url)
			source.add_header('Accept', '*/*')
			tree = ET.parse(urllib2.urlopen(source))
			break	
		# if the server breaks the connection --> reconnect and try again
		except (IOError, httplib.BadStatusLine, urllib2.HTTPError):
			if serial_stops > 25:
				return
			global stops
			stops += 1 # print how many times server breaks
			serial_stops += 1
			print "Stops = " + str(stops) + " At serial #  " + str(serial) + \
				  " where Serial_Stops = " + str(serial_stops)
			time.sleep(1.5) # wait 1.5 seconds before making another request 

	return tree

# method checks the given tree if an attorney exists
# returns this result as a boolean and the name of the attorney if true
# returns list of the desired info
def check_for_attorney(tree):

	results = {"AttorneyPresent" : False, "AttorneyName" : ""}
	person_node = tree.xpath('/tmk:Transaction/tmk:TrademarkTransactionBody \
							  /tmk:TransactionContentBag/tmk:TransactionData \
							  /tmk:TrademarkBag/tmk:Trademark \
							  /tmk:RecordAttorney/com:Contact/com:Name \
							  /com:PersonName/com:PersonFullName', \
							  namespaces = {'tmk': ns_tmk, 'com': ns_com})
							  # this is the xpath to the attorney name node

	try:		# if the attorney is present
		is_there = True
		attorney_name = person_node[0].text

	except IndexError:		# if the attorney is not present
		is_there = False
		attorney_name = ''

	results["AttorneyPresent"] = is_there
	results["AttorneyName"] = attorney_name
	return results

# collects all data from xml tree starting at the node defined by path_initial
# returns the data as a dictionary
# returns a dictionary with the parsed info stored
def load_data(tree, path_initial):
	info = {}
	path = path_initial

	try:
		root = tree.xpath(path, namespaces={'tmk': ns_tmk, 'com': ns_com})

		for element in root[0].iter():
			# add is the tag of the new piece of info to be added to the info{}
			# add will be the key, and the new data will be the value
			if ns_com2 in element.tag:
				# get rid of namespace from tag
				add = element.tag.replace(ns_com2, '') 
			if ns_tmk2 in element.tag:
				# get rid of namespace from tag
				add = element.tag.replace(ns_tmk2, '') 

			try:
				# gets rid of unnecessary new lines
				if '\n' in element.text:
					info[add] = ''
				# adds the appropriate text otherwise
				else:

					# if this  key, add, already has a defined value
					if (add in info and ('AddressLineText' in add)): 
						# add this new value to old one
						info['AddressLineText2'] = element.text
					elif(add in info):
						pass
					else:
						info[add] = element.text

			except TypeError: # simplify this jumbled code in this exception 
				try:
					if (info[add] != ''):
						pass
					else:
						info[add] = ''
				except KeyError:
					info[add] = ''
	except IndexError, AttributeError:
		pass

	return info

# identical to load_data(), except this method handles tags that are repeated
# throughout the xml tree within a certain start_node defined by path_initial
# returns a dictionary with the parsed data stored
def load_rep(tree, path_initial, element_set):
	info = {}
	path = path_initial
	root = tree.xpath(path, namespaces={'tmk': ns_tmk, 'com': ns_com})
	past_tag = ''

	elements = element_set
	elements_without_first = elements[1:]
	sub_elements = elements

	# prepare the info dictionary will all the right keys
	# inserts a list at each key to store each repeated value encountered
		# in the tree
	for item in elements:
		info[item] = []


	try:
		for element in root[0].iter():
			# add is the tag of the new piece of info to be added to the info{}
			# add will be the key, and the new data will be the value
			if ns_com2 in element.tag:
				# get rid of namespace from tag
				add = element.tag.replace(ns_com2, '') 
			if ns_tmk2 in element.tag:
				# get rid of namespace from tag
				add = element.tag.replace(ns_tmk2, '') 

			try:
				# to take care of duplicate tags one after the other per loop
				if (past_tag == add):
					if 'EntityName' == add:
						info['EntityNameCategory'].append(element.text)
						past_tag = 'EntityNameCategory'
						pass
					if 'AddressLineText' == add:
						info['AddressLineText2'].append(element.text)
						past_tag = 'AddressLineText2'
						pass
				else:
					if add in elements:
						info[add].append(element.text)
						past_tag = add

				# a gap is a tag that has no data, but should should thus have 
				# a value of '' to indicate this instead of a null data type

				# fill gaps for goods and services table
				if 'ClassificationKindCode' in elements: 
					if ((add in elements_without_first) \
						 and len(info[elements[0]]) >= 1):
						index = len(info[elements[0]]) - 1
						for item in elements_without_first:
							
							try:
								sample = info[item][index]
								# print sample
							except IndexError:
								info[item].append('')

				# fill gaps for other cases
				else: 
					if ((add in elements_without_first) \
						 and len(info[elements[0]]) >= 1):
						index = len(info[elements[0]]) - 1
						end = elements.index(past_tag)
						sub_elements = elements[0:end]
						for item in sub_elements:
							try:
								sample = info[item][index]
								# print sample
							except IndexError:
								info[item].append('')

			# if no text at all there, add blank at that tag
			except (TypeError, KeyError):
				info[past_tag].append('') # does program even pass here??
				print 'here'
	except IndexError:
		pass

	return info


#  This method prints out the tally information for ranking the most 
#  repeats of attorneys within trademark applications filed. Here, the 
#  total repeats given a certain email address and full name are 
#  printed out to another csv file.
#  no return type
def show_tally(table, max_tally):

	output = open('tally_out.csv', 'w').close() # clear the existing file
	output = open('tally_out.csv', 'r+')
	to_write = 'TallyOfRepeats ; Email ; AttorneyName' + '\n'
	write(to_write, output)
	while max_tally != 0: # prints all tally information
		for key in table:
			if table[key][1] == max_tally:
				to_write = str(table[key][1]) + '; ' + key + '; ' + \
				           table[key][0] + '\n'
				write(to_write, output)
		max_tally -= 1
