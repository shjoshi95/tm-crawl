#to do: for app date col in trademark_columns, normalize the dates!
#remove duplicate columsn from around the database...like OSN
	#transfer all changes to the mini-database If app...

import urllib2   #used to request info from url's
from lxml import etree as ET   #xml parsing module
import re 					   #regular expression module
import time					   #time tracking module
from storage6 import insert
import httplib

ns_tmk = 'http://www.wipo.int/standards/XMLSchema/Trademark/1'	#namespace 1
ns_com = 'http://www.wipo.int/standards/XMLSchema/Common/1'		#namespace 2
ns_tmk2 = '{http://www.wipo.int/standards/XMLSchema/Trademark/1}'	#{ns_tmk2}
ns_com2 = '{http://www.wipo.int/standards/XMLSchema/Common/1}'		#{ns_com2}
url_part1 = 'https://tsdrapi.uspto.gov/ts/cd/casestatus/sn'		#url segment 1
url_part2 = '/info.xml'	#url segment 2

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
stops = 0	#tracks number of server disconnections

def traverse(span):
	for trademark in span:
		tree = make_tree(trademark)
		data = load_data(tree, path_start_standard)
		mark_data = load_rep(tree, path_start_mark, mark_elements)
		gs_bag_data = load_rep(tree, path_start_gs_bag, gs_elements)
		national_cor_data = load_data(tree, path_start_national_cor)
		record_attorney_data = load_data(tree, path_start_record_attorney)
		applicant_data = load_rep(tree, path_start_applicant, \
								  applicant_elements)


		to_insert = [data, single_elements, mark_data, mark_elements, \
					 gs_bag_data, gs_elements, national_cor_data, \
					 national_cor_elements, record_attorney_data, \
					 record_attorney_elements, applicant_data, \
					 applicant_elements]
		insert(to_insert)

def write(to_write, output):
	try:
		output.write(to_write)
	except UnicodeEncodeError:
		to_write = to_write.encode('utf-8')
		output.write(to_write)

def make_tree(serial):
	'''This method contructs a unique url based on the serial provided. \
	   The tree then parses all the information from the url. If the \
	   server unplugs the program user, then the method waits 1.5 seconds \
	   before trying again, and will continue to run until the server \
	   provides all the information. The variable stops will keep track of \
	   every time the server unplugs the user.'''

	url = url_part1 + str(serial) + url_part2 #create unique url with serial 
	serial_stops = 0
	while True:
		try:
			source = urllib2.Request(url)
			source.add_header('Accept', '*/*')
			tree = ET.parse(urllib2.urlopen(source))
			break	
		except (IOError, httplib.BadStatusLine, urllib2.HTTPError): #if the server breaks the connection --> keep running
			if serial_stops > 25:
				return
			global stops
			stops += 1 #print how many times this happens
			serial_stops += 1
			print "Stops = " + str(stops) + " At serial # " + str(serial) + \
				  " where Serial_Stops = " + str(serial_stops)
			time.sleep(1.5) #wait 1.5 seconds before making another request 

	return tree

def check_for_attorney(tree):
	'''This method checks the xml tree queried and returns whether or 
	   not an attorney exists in a trademark being searched. If an 
	   attorney is their, his or her name is also returned. '''

	results = {"AttorneyPresent" : False, "AttorneyName" : ""}
	person_node = tree.xpath('/tmk:Transaction/tmk:TrademarkTransactionBody \
							  /tmk:TransactionContentBag/tmk:TransactionData \
							  /tmk:TrademarkBag/tmk:Trademark \
							  /tmk:RecordAttorney/com:Contact/com:Name \
							  /com:PersonName/com:PersonFullName', \
							  namespaces = {'tmk': ns_tmk, 'com': ns_com})
							  #this is the xpath to the attorney name node

	try:		#if the attorney is present
		is_there = True
		attorney_name = person_node[0].text

	except IndexError:		#if the attorney is not present
		is_there = False
		attorney_name = ''

	results["AttorneyPresent"] = is_there
	results["AttorneyName"] = attorney_name
	return results

def load_data(tree, path_initial):
	info = {}
	path = path_initial

	try:
		root = tree.xpath(path, namespaces={'tmk': ns_tmk, 'com': ns_com})
		for element in root[0].iter():
			if ns_com2 in element.tag:
				add = element.tag.replace(ns_com2, '') #get rid of namespace from tag
			if ns_tmk2 in element.tag:
				add = element.tag.replace(ns_tmk2, '') #get rid of namespace from tag

			try:
				if '\n' in element.text:	#gets rid of unnecessary new lines
					info[add] = ''
				else:	#adds the appropriate text otherwise

					if (add in info and ('AddressLineText' in add)):  #if the key, add, already has a defined value
						info['AddressLineText2'] = element.text #add this new value to old one
					elif(add in info):
						pass
					else:
						info[add] = element.text

			except TypeError: #simplify this jumbled code in this exception later
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


def load_rep(tree, path_initial, element_set):
	info = {}
	path = path_initial
	root = tree.xpath(path, namespaces={'tmk': ns_tmk, 'com': ns_com})
	past_tag = ''

	elements = element_set
	elements_without_first = elements[1:]
	sub_elements = elements

	for item in elements:
		info[item] = []


	try:
		for element in root[0].iter():
			if ns_com2 in element.tag:
				add = element.tag.replace(ns_com2, '') #get rid of namespace from tag
			if ns_tmk2 in element.tag:
				add = element.tag.replace(ns_tmk2, '') #get rid of namespace from tag

			try:

				if (past_tag == add): #to take care of duplicate tags one after the other in a single repetiton
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

				if 'ClassificationKindCode' in elements: #fill gaps for gs
					if ((add in elements_without_first) \
						 and len(info[elements[0]]) >= 1):
						index = len(info[elements[0]]) - 1
						for item in elements_without_first:
							
							try:
								sample = info[item][index]
								#print sample
							except IndexError:
								info[item].append('')

				else: #fill gaps for other cases
					if ((add in elements_without_first) \
						 and len(info[elements[0]]) >= 1):
						index = len(info[elements[0]]) - 1
						end = elements.index(past_tag)
						sub_elements = elements[0:end]
						for item in sub_elements:
							try:
								sample = info[item][index]
								#print sample
							except IndexError:
								info[item].append('')

			except (TypeError, KeyError): #if no text at all there, add blank at that tag
				info[past_tag].append('') #does program even pass here??
				print 'here'
	except IndexError:
		pass

	#if 'LegalEntityName' in elements:
	#	for i in range(len(elements)):
	#		print len(info[elements[i]])
	#		print info[elements[i]]

	return info

def show_tally(table, max_tally):
	'''This method prints out the tally information for ranking the most 
	   repeats of attorneys within trademark applications filed. Here, the 
	   total repeats given a certain email address and full name are 
	   printed out to another csv file.'''

	output = open('tally_out.csv', 'w').close() #clear the existing file
	output = open('tally_out.csv', 'r+')
	to_write = 'TallyOfRepeats ; Email ; AttorneyName' + '\n'
	write(to_write, output)
	while max_tally != 0: #prints all tally information
		for key in table:
			if table[key][1] == max_tally:
				to_write = str(table[key][1]) + '; ' + key + '; ' + \
				           table[key][0] + '\n'
				write(to_write, output)
		max_tally -= 1
