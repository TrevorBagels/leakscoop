

DB:				The name of the mongoDB database
COLL:			The name of the database's collection to search
Description:	A description of the database, where it came from, etc
Options: use this to set the default options for fields
	upper:					sets the field to uppercase (false)
	lower:					sets the field to lowercase (false)
	title:					sets the field to titlecase (false)
	space_to_underscore:	changes spaces to underscores (false)
	formatstr:					only for some fields, can be used to format the field with a string (default = None)
	exclude_symbols:		removes symbols, keeping only a-z 0-9 in the string (false)
	remove_spaces:			removes spaces (false)
	hashed:					used to tell if a value is hashed (false)
	multi:					set this to true if the field you're indexing will be a list instead of a single value. for instance, if someone has multiple phone numbers stored in an array, you'd set this to true. (false)
	


Fields: A list of fields that can be searched



Field
	most fields:
		key:	The key to search for in the database
		keylist:	If a document might have multiple keys for a single field that we want to search for, use "keylist" instead of "key", and provide a list of keys.




	firstname:
		the person's first name
	middlename:
		the person's middle name
	lastname:
		the person's last name
	
	address:
		the person's address. default format looks like this: "{buildingnumber} {streetname} {streettypelong} {city} {state} {zipcode}"
		note: the "formatstr" field can be added/edited to modify the format of the address.

	streetdirection:
		the direction of the street (NE, NW, SE, SW)
	streetdirectionlong:
		the direction of the street in long format (northeast, northwest, southeast, southwest)
	streetname:
		the name of the street. if a street is something like "wallnut st", the streetname is "wallnut"
	streettype:
		the type of street (ST, PL, CT, RD, etc)
	streettypelong:
		the type of street (Street, Place, Court, Road, etc)
	buildingnumber:
		the building number for the address
	zipcode:
		the zipcode for this address
	city:
		the city for the address
	state:
		the state for the address (abbreviated)
	statelong:
		the full name of the state for the address
	
	email:
		the email for this person
	username:
		the username for this person
	
	phone:
		the phone number for this person
	
	dob:
		the date of birth for this person "{dobyear}/{dobmonth}/{dobday}"
	
	dobyear:
		the year this person was born
	dobmonth:
		the month this person was born
	dobday:
		the day this person was born
	
	password:
		the password this person uses.
	
	vrn:
		vehicle registration number (license plate number)
	
	ssn:
		social security number
	
	

	
