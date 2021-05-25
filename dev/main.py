
from typing import ForwardRef

from pymongo.message import query
from . import utils
from .prodict import Prodict

class FieldOptions(Prodict):
	upper:				bool
	lower:				bool
	title:				bool
	space_to_underscore:	bool
	formatstr:			str
	exclude_symbols:	bool
	remove_spaces:		bool
	hashed:				bool
	multi:				bool
	
	def init(self):
		self.upper 				= False
		self.lower 				= False
		self.title 				= False
		self.space_to_underscore= False
		self.exclude_symbols	= False
		self.remove_spaces		= False
		self.hashed				= False
		self.multi				= False
		self.format				= ""

class Field(Prodict):
	key:			str
	keylist:		list[str]
	options:		FieldOptions
	def init(self):
		self.options = FieldOptions()

class Fields:
	firstname:		Field
	middlename:		Field
	lastname:		Field
	address:		Field

	streetdirection:	Field
	streettype:			Field
	streetname:			Field
	streettypelong:		Field
	buildingnumber:		Field
	zipcode:				Field
	city:				Field
	state:				Field

	phone:				Field
	
	dob:				Field
	dobyear:			Field
	dobmonth:			Field
	dobday:				Field

	password:			Field
	vrn:				Field
	ssn:				Field
	


class Collection(Prodict):
	DB:				str
	COLL:			str
	Description:	str
	Options:		FieldOptions
	Fields:			dict[str, Field]


import pymongo


class Main:
	def __init__(self):
		self.CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")


		self.collections:list[Collection] = [Collection.from_dict(x) for x in utils.load_json("./collections.json")]
		defOptions = FieldOptions()
		for coll in self.collections:
			for fname, field in coll.Fields.items():
				newoptions = FieldOptions()
				for o in newoptions:
					if defOptions[o] != coll.Options[o]: #the options set for ALL fields in this collection are different than default
						newoptions[o] = coll.Options[o]
					if o in field: #we've assigned this option to this field
						newoptions[o] = field[o]
				field.options = newoptions
		
		
	def address_lookup(self, building, direction, streetname, streettype, city, state, zipcode):
		query = dict(zip(
			["buildingnumber", "streetdirection", "streetname", "streettype", "city", "state", "zipcode"],
			[building, direction, streetname, streettype, city, state, zipcode]
		))
		self.lookup(query)

	def name_lookup(self, first, middle, last):
		query = dict(zip(["firstname", "middlename", "lastname"], [first, middle, last]))
		for x in query.copy():
			if query[x] == "":
				del query[x]
		self.lookup(query)

	def convert(self, value, options:FieldOptions, data:dict):
		if options.upper: value = str(value).upper()
		if options.lower: value = str(value).lower()
		if options.title: value = str(value).title()
		if options.space_to_underscore: value = str(value).replace(" ", "_")
		if options.exclude_symbols:
			for x in ["-", "(", ")", "+", "=", "|"]: value = str(value).replace(x, "")
		if options.remove_spaces: value = str(value).replace(" ", "")

		if options.formatstr != None:
			value = options.formatstr
			for k, x in data.items():
				if type(x) == str:
					value = value.replace("{" + k + "}", x)
		return value

	def lookup(self, parameters):
		results = []
		for collection in self.collections:
			print("Searching through", collection.Description)
			q = {}
			for k, v in parameters.items():
				if k in collection.Fields:
					converted = self.convert(v, collection.Fields[k].options, parameters)
					if converted != "":
						q[collection.Fields[k].key] = converted
			if len(q) == 0:
				continue
			print("Query:", q)

			if self.CLIENT.get_database(collection.DB) == None:
				print("Database does not exist!")
				continue
			elif collection.COLL not in self.CLIENT[collection.DB].collection_names():
				print("Collection does not exist!")
				continue
			result = self.CLIENT[collection.DB][collection.COLL].find_one(q)
			if result != None:
				print("Found something! ")
				results.append({"DB": collection.DB, "COLL": collection.COLL, "DESC": collection.Description, "data": result})
		
		utils.save_json("lookup.json", results)
			

	
					