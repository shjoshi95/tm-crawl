#TODO
#normalize phone numbers
#should some varchars varchars in table creation become text?
#fix the date problem with the 00 as the day in 86080970(day)/86182018(month) firstuseddate
#check trademark.id in the insert into mark_event
#should application date stay in the trademark_lawyer table; if so, delete 
	#this from trademark, else delete application date from trademark_lawyer
	#do the same for the mark_event_date from trademark_mark_event
#delete columns from current basis and trademark_current basis that have no data
#add semi colons to ends of insert into statements?
#for the cross join sections, should I provide explicit table cast names (i.e
	#table.columnname rather than just the column name if both tables have the same column.)




#Formatting:
#in create table statements make all data types uniform with longest string
#make all table names singular
#take out all redundant clauses like info and data in var names
#make the column names simpler

import psycopg2 #required for python --> postgres connection
import re  		#required for regular expression manipulation
import settings	#settings for database connectivity

def insert(inserted):

	global data
	data = inserted[0]
	single_elements = inserted[1]
	mark_data = inserted[2]
	mark_elements = inserted[3]
	gs_bag_data = inserted[4]
	gs_elements = inserted[5]
	national_cor_data = inserted[6]
	national_cor_elements = inserted[7]
	record_attorney_data = inserted[8]
	record_attorney_elements = inserted[9]
	applicant_data = inserted[10]
	applicant_elements = inserted[11]
	nat_trade_data = inserted[12]
	nat_trade_elements = inserted[13]

	conn = psycopg2.connect(database = settings.database(), 
							user = settings.user(), 
							password = settings.password()) #Connect database
	
	data = proof_data(data, single_elements)
	mark_data = proof_data(mark_data, mark_elements)
	gs_bag_data = proof_data(gs_bag_data, gs_elements)
	national_cor_data = proof_data(national_cor_data, national_cor_elements)
	record_attorney_data = proof_data(record_attorney_data, 
									  record_attorney_elements)
	applicant_data = proof_data(applicant_data, applicant_elements)
	nat_trade_data = proof_data(nat_trade_data, nat_trade_elements)

	cur = conn.cursor() #Initiate the cursor which executes postgres commands
	#cur.execute('''drop table if exists ''' + table_out +';') #Remove old table
	#make lawyer table


	print data['ApplicationNumberText']

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS lawyer 
			( 
				id                         SERIAL PRIMARY KEY, 
				attorney_name              TEXT, 
				attorney_comment           TEXT, 
				contact_name               TEXT, 
				organization_standard_name TEXT, 
				address_line_text          TEXT, 
				address_line_text_2        TEXT, 
				city_name                  TEXT, 
				geographic_region_name     VARCHAR(25), 
				country_code               VARCHAR(25), 
				postal_code                VARCHAR(25), 
				email_address_text         TEXT, 
				phone_number               VARCHAR(25), 
				fax_number                 VARCHAR(25), 
				website                    TEXT 
			);'''
	)

	cur.execute(
		'''INSERT INTO lawyer 
			(
				attorney_name, 
				attorney_comment, 
				contact_name, 
				organization_standard_name, 
				address_line_text, 
				address_line_text_2, 
				city_name, 
				geographic_region_name, 
				country_code, 
				postal_code,
				email_address_text, 
				phone_number, 
				fax_number, 
				website
			) 
			SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s 
			WHERE NOT EXISTS 
			(
				SELECT email_address_text 
				FROM lawyer 
				WHERE email_address_text LIKE %s
			)''',
			(
				record_attorney_data['PersonFullName'], 
				record_attorney_data['CommentText'], 
				national_cor_data['PersonFullName'], 
				national_cor_data['OrganizationStandardName'], 
				national_cor_data['AddressLineText'], 
				national_cor_data['AddressLineText2'], 
				national_cor_data['CityName'], 
				national_cor_data['GeographicRegionName'], 
				national_cor_data['CountryCode'], 
				national_cor_data['PostalCode'], 
				national_cor_data['EmailAddressText'], 
				national_cor_data['PhoneNumber'], 
				national_cor_data['FaxNumber'], 
				get_website(national_cor_data['EmailAddressText']), 
				national_cor_data['EmailAddressText']
			)
	)

	#make trademark table
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark 
			(		 
				id                                        SERIAL PRIMARY KEY, 
				serial_number                             INTEGER, 
				registration_office_code                  VARCHAR(5), 
				ip_office_code                            VARCHAR(5), 
				registration_number                       VARCHAR(20), 
				application_date                          DATE, 
				registration_date                         DATE, 
				filing_place                              VARCHAR(5), 
				mark_current_status_date                  DATE, 
				mark_category                             VARCHAR(25), 
				mark_feature_category                     VARCHAR(100), 
				first_used_date                           DATE, 
				blank_month_1							  BOOLEAN,
				blank_day_1								  BOOLEAN,
				first_used_commerce_date                  DATE, 
				blank_month_2							  BOOLEAN,
				blank_day_2								  BOOLEAN,
				publication_identifier                    VARCHAR(100), 
				publication_date                          DATE, 
				class_number                              VARCHAR(5), 
				goods_services_description_text           TEXT, 
				national_status_category                  TEXT, 
				national_status_code                      TEXT, 
				national_status_external_description_text TEXT
			);'''
	)


	#insert into trademark table

	cur.execute(
		'''INSERT INTO trademark 
			(
				serial_number, 
				registration_office_code, 
				IP_office_code,
				registration_number, 
				application_date, 
				registration_date, 
				filing_place, 
				mark_current_status_date, 
				mark_category, 
				mark_feature_category, 
				first_used_date, 
				blank_month_1,
				blank_day_1,
				first_used_commerce_date, 
				blank_month_2,
				blank_day_2,
				publication_identifier, 
				publication_date, 
				class_number, 
				goods_services_description_text,
				national_status_category, 
				national_status_code, 
				national_status_external_description_text
			) 
			SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
				   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
				   %s, %s, %s
		   	FROM lawyer 
		   	WHERE lawyer.email_address_text LIKE %s 
		   	AND NOT EXISTS 
		   	(
		   		SELECT serial_number 
		   		FROM trademark 
		   		WHERE serial_number = %s
	   		)''', 
			(
				data['ApplicationNumberText'], 
				data['RegistrationOfficeCode'], 
				data['IPOfficeCode'], 
				data['RegistrationNumber'], 
				get_date(data), 
				data['RegistrationDate'], 
				data['FilingPlace'], 
				data['MarkCurrentStatusDate'], 
				data['MarkCategory'], 
				data['MarkFeatureCategory'], 
				data['FirstUsedDate'], 
				data['BlankMonth1'],
				data['BlankDay1'],
				data['FirstUsedCommerceDate'], 
				data['BlankMonth2'],
				data['BlankDay2'],
				data['PublicationIdentifier'], 
				data['PublicationDate'], 
				data['ClassNumber'], 
				data['GoodsServicesDescriptionText'], 
				data['NationalStatusCategory'], 
				data['NationalStatusCode'], 
				data['NationalStatusExternalDescriptionText'], 
				national_cor_data['EmailAddressText'], 
				data['ApplicationNumberText']
			)
	)
	
	#make word_mark
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS word_mark 
			( 
				id                                   SERIAL PRIMARY KEY, 
				mark_verbal_element_text             VARCHAR(1000), 
				mark_significant_verbal_element_text VARCHAR(1000), 
				mark_standard_character_indicator    BOOLEAN 
  			); '''
	)

	#insert into word_mark
	if (data['MarkVerbalElementText'] is None):
		data['MarkVerbalElementText'] = 'No word_mark available'

	cur.execute(
		'''INSERT INTO word_mark 
			(
				mark_verbal_element_text, 
				mark_significant_verbal_element_text, 
				mark_standard_character_indicator
			) 
			SELECT %s, %s, %s 
			WHERE NOT EXISTS 
			(
				SELECT mark_verbal_element_text 
				FROM word_mark 
				WHERE mark_verbal_element_text = %s
			)''', 
			(
				data['MarkVerbalElementText'], 
				data['MarkSignificantVerbalElementText'], 
				data['MarkStandardCharacterIndicator'], 
				data['MarkVerbalElementText']
			)
	)

	#make image_mark
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS image_mark 
			( 
				id                                  SERIAL PRIMARY KEY, 
				image_file_name                     VARCHAR(1000), 
				mark_image_colour_claimed_text      TEXT, 
				mark_image_colour_part_claimed_text TEXT, 
				image_colour_indicator              BOOLEAN 
			);'''
	)

	#insert into image_mark
	
	if (data['MarkVerbalElementText'] is None):
		image_file = 'No image available'
	else:
		image_file = data['ApplicationNumberText'] + '.png'

	cur.execute(
		'''INSERT INTO image_mark 
			(
				image_file_name, 
				mark_image_colour_claimed_text, 
				mark_image_colour_part_claimed_text, 
				image_colour_indicator
			) 
			SELECT %s, %s, %s, %s 
			WHERE NOT EXISTS 
			(
				SELECT image_file_name 
				FROM image_mark 
				WHERE image_file_name = %s
			)''', 
			(
				image_file, 
				data['MarkImageColourClaimedText'], 
				data['MarkImageColourPartClaimedText'], 
				data['ImageColourIndicator'], 
				image_file
			)
	)

	#make sound_mark
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS sound_mark 
			( 
				id         SERIAL PRIMARY KEY, 
				mark_sound VARCHAR(1000) 
			);'''
	)

	#insert into sound_mark

	if (data['MarkSound'] is None):
		data['MarkSound'] = 'No sound_mark available'

	cur.execute(
		'''INSERT INTO sound_mark
			(
				mark_sound 
			)
			SELECT %s 
			WHERE NOT EXISTS 
			(
				SELECT mark_sound 
				FROM sound_mark 
				WHERE mark_sound = %s
			)''', 
			(
				data['MarkSound'], 
				data['MarkSound']
			)
	)

	#make current_basis
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS current_basis 
			( 
				id                                   SERIAL PRIMARY KEY, 
				basis_foreign_application_indicator  BOOLEAN, 
				basis_foreign_registration_indicator BOOLEAN, 
				basis_use_indicator                  BOOLEAN, 
				basis_intent_to_use_indicator        BOOLEAN, 
				no_basis_indicator                   BOOLEAN
			);'''
	)

	#insert into current_basis
	cur.execute(
		'''INSERT INTO current_basis 
			(
				basis_foreign_application_indicator, 
				basis_foreign_registration_indicator, 
				basis_use_indicator, 
				basis_intent_to_use_indicator, 
				no_basis_indicator
			) 
			SELECT %s, %s, %s, %s, %s 
			FROM trademark 
			WHERE trademark.serial_number = %s 
			AND NOT EXISTS 
			(
				SELECT
				(
					basis_foreign_application_indicator, 
					basis_foreign_registration_indicator, 
					basis_use_indicator, 
					basis_intent_to_use_indicator, 
					no_basis_indicator
				)
				FROM current_basis 
				WHERE basis_foreign_application_indicator = %s 
				AND basis_use_indicator = %s
				AND basis_intent_to_use_indicator = %s
				AND basis_foreign_registration_indicator = %s
				AND no_basis_indicator = %s
			)''', 
			(
				data['BasisForeignApplicationIndicator'], 
				data['BasisForeignRegistrationIndicator'],
				data['BasisUseIndicator'], 
				data['BasisIntentToUseIndicator'], 
				data['NoBasisIndicator'],
				data['ApplicationNumberText'],
				data['BasisForeignApplicationIndicator'],
				data['BasisUseIndicator'],
				data['BasisIntentToUseIndicator'],
				data['BasisForeignRegistrationIndicator'],
				data['NoBasisIndicator']
			)
	)

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS mark_event 
			( 
				id                          SERIAL PRIMARY KEY, 
				mark_event_category         TEXT, 
				mark_event_code             TEXT, 
				mark_event_description_text TEXT, 
				mark_event_entry_number     INTEGER, 
				mark_event_additional_text  TEXT, 
				mark_event_date             DATE
			);'''
	)

	for i in range(len(mark_data.values()[0])):

		cur.execute(
			'''INSERT INTO mark_event 
				(
					mark_event_category, 
					mark_event_code, 
					mark_event_description_text, 
					mark_event_entry_number, 
					mark_event_additional_text, 
					mark_event_date
				) 
				SELECT %s, %s, %s, %s, %s, %s 
				FROM trademark 
				WHERE trademark.serial_number = %s 
				AND NOT EXISTS 
				(
					SELECT 
					(
						mark_event_category, 
						mark_event_code, 
						mark_event_description_text, 
						mark_event_entry_number, 
						mark_event_additional_text
					)
					FROM mark_event 
					WHERE mark_event_category LIKE %s 
					AND mark_event_code LIKE %s
					AND mark_event_description_text LIKE %s 
					AND mark_event_entry_number = %s
					AND mark_event_additional_text LIKE %s
				)''', 
				(
					mark_data['MarkEventCategory'][i], 
					mark_data['MarkEventCode'][i], 
					mark_data['MarkEventDescriptionText'][i], 
					mark_data['MarkEventEntryNumber'][i], 
					mark_data['MarkEventAdditionalText'][i], 
					mark_data['MarkEventDate'][i], 
					data['ApplicationNumberText'], 
					mark_data['MarkEventCategory'][i],
					mark_data['MarkEventCode'][i],
					mark_data['MarkEventDescriptionText'][i],
					mark_data['MarkEventEntryNumber'][i],
					mark_data['MarkEventAdditionalText'][i]
				)
		)
				   
				   #Is the second trademark.id call legal? 
				   #Or do I need to do the full SELECT again?

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS gs_bag 
			( 
				id                       SERIAL PRIMARY KEY, 
				classification_kind_code VARCHAR(25), 
				class_number             INTEGER, 
				national_class_number    INTEGER
			);'''
	)

	for i in range(len(gs_bag_data.values()[0])):

		cur.execute(
			'''INSERT INTO gs_bag 
				(
					classification_kind_code, 
					class_number, 
					national_class_number
				) 
				SELECT %s, %s, %s 
				FROM trademark 
				WHERE trademark.serial_number = %s 
				AND NOT EXISTS 
				(
					SELECT 
					(
						classification_kind_code, 
						class_number,
						national_class_number
					)
					FROM gs_bag 
					WHERE classification_kind_code LIKE %s 
					AND (class_number = %s OR national_class_number = %s)
				)''', 
				(
					gs_bag_data['ClassificationKindCode'][i], 
					gs_bag_data['ClassNumber'][i], 
					gs_bag_data['NationalClassNumber'][i], 
					data['ApplicationNumberText'], 
					gs_bag_data['ClassificationKindCode'][i], 
					gs_bag_data['ClassNumber'][i], 
					gs_bag_data['NationalClassNumber'][i]
				)
		)
				   #Is the second trademark.id call legal? Or do I need to do the full SELECT again?

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS applicant 
			( 
				id                         SERIAL PRIMARY KEY, 
				legal_entity_name          TEXT, 
				national_legal_entity_code TEXT, 
				incorporation_country_code VARCHAR(25), 
				incorporation_state        VARCHAR(25), 
				organization_standard_name TEXT, 
				entity_name                TEXT, 
				entity_name_category       TEXT, 
				address_line_text          TEXT, 
				address_line_text_2        TEXT, 
				city_name                  TEXT, 
				geographic_region_name     TEXT, 
				country_code               VARCHAR(25), 
				postal_code                VARCHAR(25)
			);'''
	)

	for i in range(len(applicant_data.values()[0])):

   		cur.execute(
   			'''INSERT INTO applicant 
   				(
   					legal_entity_name, 
   					national_legal_entity_code, 
					incorporation_country_code, 
					incorporation_state, 
					organization_standard_name, 
					entity_name, 
					entity_name_category, 
					address_line_text, 
					address_line_text_2, 
					city_name, 
					geographic_region_name, 
					country_code, 
					postal_code
				) 
				SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, 
					   %s, %s, %s, %s
			   	WHERE NOT EXISTS 
				(
					SELECT 
					(
						legal_entity_name, 
						incorporation_country_code,
						incorporation_state,
						organization_standard_name,
						entity_name
					)
   					FROM applicant 
   					WHERE legal_entity_name LIKE %s
   					AND incorporation_country_code LIKE %s
   					AND incorporation_state LIKE %s
   					AND organization_standard_name LIKE %s 
   					AND entity_name LIKE %s 
				)''', 
   				(
   					applicant_data['LegalEntityName'][i], 
   					applicant_data['NationalLegalEntityCode'][i], 
					applicant_data['IncorporationCountryCode'][i], 
					applicant_data['IncorporationState'][i], 
					applicant_data['OrganizationStandardName'][i], 
					applicant_data['EntityName'][i], 
					applicant_data['EntityNameCategory'][i],
					applicant_data['AddressLineText'][i], 
					applicant_data['AddressLineText2'][i],
					applicant_data['CityName'][i], 
					applicant_data['GeographicRegionName'][i],
					applicant_data['CountryCode'][i], 
					applicant_data['PostalCode'][i], 
					applicant_data['LegalEntityName'][i],
					applicant_data['IncorporationCountryCode'][i],
					applicant_data['IncorporationState'][i], 
					applicant_data['OrganizationStandardName'][i], 
					applicant_data['EntityName'][i]
				)
		)


	cur.execute(
		'''CREATE TABLE IF NOT EXISTS national_trademark
  			(
		     id                                            SERIAL PRIMARY KEY,
		     register_category                             TEXT,
		     amended_principal_register_indicator          BOOLEAN,
		     amended_supplemental_register_indicator       BOOLEAN,
		     mark_current_status_external_description_text TEXT
  			); '''
	)

	cur.execute(
		'''INSERT INTO national_trademark
			(
				register_category,
				amended_principal_register_indicator,
				amended_supplemental_register_indicator,
				mark_current_status_external_description_text
			)
			SELECT %s, %s, %s, %s
			WHERE NOT EXISTS
			(
				SELECT
				(
					register_category,
					amended_principal_register_indicator,
					amended_supplemental_register_indicator,
					mark_current_status_external_description_text
				)
				FROM national_trademark
				WHERE register_category LIKE %s
				AND amended_principal_register_indicator = %s
				AND amended_supplemental_register_indicator = %s
				AND mark_current_status_external_description_text LIKE %s
			)''',
			(
				nat_trade_data['RegisterCategory'],
				nat_trade_data['AmendedPrincipalRegisterIndicator'],
				nat_trade_data['AmendedSupplementalRegisterIndicator'],
				nat_trade_data['MarkCurrentStatusExternalDescriptionText'],
				nat_trade_data['RegisterCategory'],
				nat_trade_data['AmendedPrincipalRegisterIndicator'],
				nat_trade_data['AmendedSupplementalRegisterIndicator'],
				nat_trade_data['MarkCurrentStatusExternalDescriptionText']
			)
	)


	#TABLE CONNECTIONS
	#TABLE CONNECTIONS
	#TABLE CONNECTIONS
	#TABLE CONNECTIONS
	#TABLE CONNECTIONS for the many-many in word, image, and sound!
	#TABLE CONNECTIONS
	#TABLE CONNECTIONS
	#TABLE CONNECTIONS
	#TABLE CONNECTIONS

	#connect trademark to word_mark
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_word_mark 
			(
				trademark_id 					INTEGER, 
				word_mark_id 					INTEGER, 
				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT word_mark_id_fk 
					FOREIGN KEY (word_mark_id) 
					REFERENCES word_mark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE
			);'''
	)
	#example with Values insert
	#cur.execute('''INSERT INTO trademark_word_mark (trademark_id, word_mark_id) VALUES 
	#			   (currval('trademark_id_seq'), currval('word_mark_id_seq'));''')

   	cur.execute(
   		'''INSERT INTO trademark_word_mark 
   			(
   				trademark_id, 
   				word_mark_id
			)
			SELECT trademark.id, word_mark.id 
			FROM trademark 
			CROSS JOIN word_mark
			WHERE serial_number = %s 
			AND mark_verbal_element_text LIKE %s 
			AND NOT EXISTS 
			(
				SELECT 
				(
					trademark_id, 
					word_mark_id 
				)
   				FROM trademark_word_mark
				WHERE trademark_id = trademark.id 
				AND word_mark_id = word_mark.id
			)''',
   			(
   				data['ApplicationNumberText'], 
   				data['MarkVerbalElementText']
			)
	) 

   	#note, the argument list must always be a LIST (even single tuple)!
	#id FROM trademark WHERE serial_number = %s

	#connect trademark to image_mark
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_image_mark 
			(
				trademark_id 					INTEGER, 
				image_mark_id 					INTEGER, 
				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT image_mark_id_fk 
					FOREIGN KEY (image_mark_id) 
					REFERENCES image_mark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE
			);'''
	)

	cur.execute(
		'''INSERT INTO trademark_image_mark 
			(
				trademark_id, 
				image_mark_id
			)
			SELECT trademark.id, image_mark.id 
			FROM trademark 
			CROSS JOIN image_mark
			WHERE serial_number = %s 
			AND image_file_name LIKE %s 
			AND NOT EXISTS 
			(
				SELECT 
				(
					trademark_id, 
					image_mark_id 
				)
				FROM trademark_image_mark
				WHERE trademark_id = trademark.id 
				AND image_mark_id = image_mark.id
			)''', 
			(
				data['ApplicationNumberText'], 
				image_file
			)
	) 

    #connect trademark to sound_mark
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_sound_mark 
			(
				trademark_id 					INTEGER, 
				sound_mark_id 					INTEGER, 
				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT sound_mark_id_fk 
					FOREIGN KEY (sound_mark_id) 
					REFERENCES sound_mark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE
			);'''
	)

	cur.execute(
		'''INSERT INTO trademark_sound_mark 
			(
				trademark_id, 
				sound_mark_id
			)
			SELECT trademark.id, sound_mark.id 
			FROM trademark 
			CROSS JOIN sound_mark
			WHERE serial_number = %s 
			AND mark_sound LIKE %s 
			AND NOT EXISTS 
			(
				SELECT 
				(
					trademark_id, 
					sound_mark_id 
				)
				FROM trademark_sound_mark
				WHERE trademark_id = trademark.id 
				AND sound_mark_id = sound_mark.id
			)''', 
			(
				data['ApplicationNumberText'], 
				data['MarkSound']
			)
	) 	

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_lawyer
			(
				trademark_id 					INTEGER,
				lawyer_id 						INTEGER,
				application_date 				DATE,
				CONSTRAINT trademark_id_fk
					FOREIGN KEY (trademark_id)
					REFERENCES trademark (id)
					MATCH SIMPLE
					ON UPDATE CASCADE
					ON DELETE CASCADE,
				CONSTRAINT lawyer_id_fk
					FOREIGN KEY (lawyer_id)
					REFERENCES lawyer (id)
					MATCH SIMPLE
					ON UPDATE CASCADE
					ON DELETE CASCADE
			);'''
	)
	
	cur.execute(
		'''INSERT INTO trademark_lawyer
			(
				trademark_id,
				lawyer_id,
				application_date
			)
			SELECT trademark.id, lawyer.id, %s
			FROM trademark
			CROSS JOIN lawyer
			WHERE serial_number = %s 
			AND email_address_text LIKE %s
			AND NOT EXISTS
			(
				SELECT
				(
					trademark_id,
					lawyer_id,
					application_date
				)
				FROM trademark_lawyer
				WHERE trademark_id = trademark.id
				AND lawyer_id = lawyer.id
				AND application_date = %s
			);''',
			(
				get_date(data),
				data['ApplicationNumberText'],
				national_cor_data['EmailAddressText'],
				get_date(data)
			)
	)

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_current_basis
			(
				trademark_id 						INTEGER,
				current_basis_id 					INTEGER,
				CONSTRAINT trademark_id_fk
					FOREIGN KEY (trademark_id)
					REFERENCES trademark (id)
					MATCH SIMPLE
					ON UPDATE CASCADE
					ON DELETE CASCADE,
				CONSTRAINT current_basis_id_fk
					FOREIGN KEY (current_basis_id)
					REFERENCES current_basis (id)
					MATCH SIMPLE
					ON UPDATE CASCADE
					ON DELETE CASCADE
			);'''
	)

	cur.execute(
		'''INSERT INTO trademark_current_basis
			(
				trademark_id,
				current_basis_id
			)
			SELECT trademark.id, current_basis.id
			FROM trademark 
			CROSS JOIN current_basis
			WHERE serial_number = %s
			AND basis_foreign_application_indicator = %s
			AND basis_use_indicator = %s
			AND basis_intent_to_use_indicator = %s
			AND basis_foreign_registration_indicator = %s
			AND no_basis_indicator = %s
			AND NOT EXISTS
			(
				SELECT
				(
					trademark_id,
					current_basis_id
				)
				FROM trademark_current_basis
				WHERE trademark_id = trademark.id
				AND current_basis_id = current_basis.id
			)''',
			(
				data['ApplicationNumberText'],
				data['BasisForeignApplicationIndicator'],
				data['BasisUseIndicator'],
				data['BasisIntentToUseIndicator'],
				data['BasisForeignRegistrationIndicator'],
				data['NoBasisIndicator']
			)
	)

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_mark_event
			(
				trademark_id 					INTEGER,
				mark_event_id 					INTEGER,
				mark_event_date 				DATE,
				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT mark_event_id_fk
					FOREIGN KEY (mark_event_id) 
					REFERENCES mark_event (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE 
			);'''
	)

	for i in range(len(mark_data.values()[0])):

		cur.execute(
			'''INSERT INTO trademark_mark_event
				(
					trademark_id,
					mark_event_id,
					mark_event_date
				)
				SELECT trademark.id, mark_event.id, %s
				FROM trademark 
				CROSS JOIN mark_event
				WHERE serial_number = %s 
				AND mark_event_category LIKE %s
				AND mark_event_code LIKE %s
				AND mark_event_description_text LIKE %s
				AND mark_event_entry_number = %s
				AND mark_event_additional_text LIKE %s
				AND NOT EXISTS 
				(
					SELECT 
					(
						trademark_id,
						mark_event_id,
						mark_event_date
					)
					FROM trademark_mark_event
					WHERE trademark_id = trademark.id 
					AND mark_event_id = mark_event.id
					AND mark_event_date = %s
				)''', 
				(
					mark_data['MarkEventDate'][i],
					data['ApplicationNumberText'],
					mark_data['MarkEventCategory'][i],
					mark_data['MarkEventCode'][i],
					mark_data['MarkEventDescriptionText'][i],
					mark_data['MarkEventEntryNumber'][i],
					mark_data['MarkEventAdditionalText'][i],
					mark_data['MarkEventDate'][i]
				)
		)

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_gs_bag
			(
				trademark_id 					INTEGER,
				gs_bag_id 						INTEGER,

				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT gs_bag_id_fk
					FOREIGN KEY (gs_bag_id) 
					REFERENCES gs_bag (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE 
			);'''
	)

	for i in range(len(gs_bag_data.values()[0])):

		cur.execute(
			'''INSERT INTO trademark_gs_bag
				(
					trademark_id,
					gs_bag_id
				)
				SELECT trademark.id, gs_bag.id
				FROM trademark 
				CROSS JOIN gs_bag
				WHERE serial_number = %s 
				AND classification_kind_code LIKE %s
				AND (gs_bag.class_number = %s OR national_class_number = %s)
				AND NOT EXISTS 
				(
					SELECT 
					(
						trademark_id,
						gs_bag_id
					)
					FROM trademark_gs_bag
					WHERE trademark_id = trademark.id 
					AND gs_bag_id = gs_bag.id
				)''', 
				(
					data['ApplicationNumberText'],
					gs_bag_data['ClassificationKindCode'][i],
					gs_bag_data['ClassNumber'][i],
					gs_bag_data['NationalClassNumber'][i]
				)
		)

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_applicant
			(
				trademark_id 					INTEGER,
				applicant_id 					INTEGER,
				applicant_role 					TEXT,
				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT applicant_id_fk 
					FOREIGN KEY (applicant_id) 
					REFERENCES applicant (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE 
			);'''
	)

	for i in range(len(applicant_data.values()[0])):

		cur.execute(
			'''INSERT INTO trademark_applicant
				(
					trademark_id,
					applicant_id,
					applicant_role
				)
				SELECT trademark.id, applicant.id, %s
				FROM trademark 
				CROSS JOIN applicant
				WHERE serial_number = %s 
				AND incorporation_country_code LIKE %s
				AND incorporation_state LIKE %s
				AND organization_standard_name LIKE %s
				AND entity_name LIKE %s
				AND postal_code LIKE %s
				AND NOT EXISTS 
				(
					SELECT 
					(
						trademark_id, 
						applicant_id,
						applicant_role 
					)
					FROM trademark_applicant
					WHERE trademark_id = trademark.id 
					AND applicant_id = applicant.id
					AND applicant_role = %s
				)''', 
				(
					applicant_data['CommentText'][i],
					data['ApplicationNumberText'],
					applicant_data['IncorporationCountryCode'][i],
					applicant_data['IncorporationState'][i],
					applicant_data['OrganizationStandardName'][i],
					applicant_data['EntityName'][i],
					applicant_data['PostalCode'][i],
					applicant_data['CommentText'][i]
				)
		)

	cur.execute(
		'''CREATE TABLE IF NOT EXISTS trademark_national_trademark
			(
				trademark_id 							INTEGER,
				national_trademark_id 					INTEGER,
				CONSTRAINT trademark_id_fk 
					FOREIGN KEY (trademark_id) 
					REFERENCES trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE, 
				CONSTRAINT national_trademark_id_fk
					FOREIGN KEY (national_trademark_id) 
					REFERENCES national_trademark (id) 
					MATCH SIMPLE 
					ON UPDATE CASCADE 
					ON DELETE CASCADE 
			);'''
	)

	cur.execute(
		'''INSERT INTO trademark_national_trademark
			(
				trademark_id,
				national_trademark_id
			)
			SELECT trademark.id, national_trademark.id
			FROM trademark 
			CROSS JOIN national_trademark
			WHERE serial_number = %s
			AND register_category LIKE %s
			AND amended_principal_register_indicator = %s
			AND amended_supplemental_register_indicator = %s
			AND mark_current_status_external_description_text LIKE %s
			AND NOT EXISTS
			(
				SELECT
				(
					trademark_id,
					national_trademark_id
				)
				FROM trademark_national_trademark
				WHERE trademark_id = trademark.id
				AND national_trademark_id = national_trademark.id
			)''',
			(
				data['ApplicationNumberText'],
				nat_trade_data['RegisterCategory'],
				nat_trade_data['AmendedPrincipalRegisterIndicator'],
				nat_trade_data['AmendedSupplementalRegisterIndicator'],
				nat_trade_data['MarkCurrentStatusExternalDescriptionText']
			)
	)

	#insert into ^ this table now with the appropriate values and take out
	#trademark_id and comment text from the applicant table!
	

	conn.commit() #validate all changes and communicate them to postgres
	conn.close()


























def convert(index, contents):
	'''This method takes in an index to read in the string contents. 
	Because each row may or may not have an element in the TM5 
	column, this method considers the cases of whether it does or 
	not and calculates the values of fifth_in, sixth_in, and 
	seventh_in, (the inputs to the table's database), and returns 
	them in a list called response.'''

	if (contents[index] != 'T' and contents[index] != 't'): #if there is no T
		fifth_in = ''
		find = re.match('(\d)*'+'/(\d)*/'+ '(\d)*' + ' ', contents[index:])
		date = find.group() #extract contents from regular expression above
		revise = contents[index:].replace(date, '')

	else: #if there is a T
		fifth_in = 'T'
		find = re.match('(\d)*'+'/.*/'+ '(\d)*' + ' ', contents[(index+2):])
		date = find.group()
		revise = contents[(index+2):].replace(date, '')

	sixth_in = date
	seventh_in = revise
	response = [fifth_in, sixth_in, seventh_in] #list of desired values
	return response

def proof_data(data, tags):
	
	dates = ['ApplicationDate', 'RegistrationDate', 'MarkCurrentStatusDate', 
			 'FirstUsedDate', 'FirstUsedCommerceDate', 'PublicationDate', 
			 'MarkEventDate']
	booleans = ['MarkStandardCharacterIndicator', 'ImageColourIndicator', 
				'BasisForeignApplicationIndicator', 'BasisUseIndicator', 
				'BasisForeignRegistrationIndicator', 'NoBasisIndicator', 
				'BasisIntentToUseIndicator']
	numbers = ['MarkEventEntryNumber', 'ClassNumber', 'NationalClassNumber']

	could_be_none = [dates, booleans, numbers]
	required_tags = tags
	
	#Add these override columsn when dates have 00 elements
	if ('ApplicationNumberText' in tags):
		data['BlankMonth1'] = 'false' 	
		data['BlankDay1'] = 'false'	
		data['BlankMonth2'] = 'false'
		data['BlankDay2'] = 'false'		

	for i in range(len(required_tags)):

		try:
			sample = data[required_tags[i]]
			if (type(sample) == list):
				for j in range(len(data.values()[0])):
					if (data[required_tags[i]][j] == '' and 
						check_none(could_be_none, required_tags[i])):
						data[required_tags[i]][j] = None

		except KeyError:
			
			if (check_none(could_be_none, required_tags[i])):
				data[required_tags[i]] = None
				sample = ''

			else:
				data[required_tags[i]] = ''
				sample = ''

		if ((required_tags[i] == 'FirstUsedDate' or 
			 required_tags[i] == 'FirstUsedCommerceDate') and
			 data[required_tags[i]] is not None):

			if (type(sample) == list):
				for j in range(len(data.values()[0])):
					value = data[required_tags[i]][j]
					data[required_tags[i]][j] = format_date(value, 
															required_tags[i])
			else:
				value = sample
				data[required_tags[i]] = format_date(value, required_tags[i])


	return data

#def format_phone_number(given_number):


def format_date(given_date, key): #for unformatted dates, and dates w/o times

	year = given_date[:4]
	month = given_date[4:6]
	day = given_date[6:]

	if (day == '00' or month == '00'):
		new_date = year + '-' + '01' + '-' + '01'
		if (key == 'FirstUsedDate'):
			if (month == '00'):
				data['BlankMonth1'] = 'true' #if firstuseddate month = '00'
			if (day == '00'):
				data['BlankDay1'] = 'true' #if firstuseddate day = '00'
		if (key in 'FirstUsedCommerceDate'):
			if (month == '00'):
				data['BlankMonth2'] = 'true' #if firstcommercedate month = '00'
			if (day == '00'):
				data['BlankDay2'] = 'true' #if firstcommercedate month = '00'
	else:
		new_date = year + '-' + month + '-' + day

	return new_date 

	#except KeyError: #for when a tag is missing altogether
	#print 'here' + ' ' + required_tags[i]
	#	return None

def check_none(could_be_none, key):
	result = False

	for i in range(len(could_be_none)):
		if (key in could_be_none[i]):
			result = True

	return result

def get_date(data):
	'''This method finds and returns the application date from the 
	   serial number used within the XML tree.'''

	try:
		date_initial = data['ApplicationDate']
		if (date_initial is None):
			date_initial = ''
	except IndexError:
		date_initial = ''

	date_middle = re.match('.*-.*-.*-', date_initial) #collect date segment
	try:
		date = date_middle.group()
		date = date[:-1] #chop off extra char (last one)
	except AttributeError:
		date = None
	return date

def get_website(email):
	try:
		get_web = re.match('.*@', email) #print site name
		scrap = get_web.group()
		website = email.replace(scrap, '')
	except AttributeError:
		website = None

	return website

def last(string_in):
	#This method returns the last character of the string inputted
	return string_in[len(string_in) - 1]