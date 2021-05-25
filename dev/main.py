
from typing import ForwardRef

from pymongo.message import query
from . import utils
from .prodict import Prodict

class FieldOptions(Prodict):
	upper:				bool
	lower:				bool
	title:				bool
	space_to_underscore:bool
	formatstr:			str
	formatphone:		str
	exclude_symbols:	bool
	remove_spaces:		bool
	hashed:				bool
	multi:				bool
	textsearch:			bool
	
	def init(self):
		self.upper 				= False
		self.lower 				= False
		self.title 				= False
		self.space_to_underscore= False
		self.exclude_symbols	= False
		self.remove_spaces		= False
		self.hashed				= False
		self.multi				= False
		self.formatstr			= None
		self.formatphone		= None
		self.textsearch			= False

class Field(Prodict):
	key:			str
	keylist:		list[str]
	options:		FieldOptions
	def init(self):
		self.options = FieldOptions()

class Fields:
	firstname:			Field
	middlename:			Field
	lastname:			Field
	address:			Field

	streetdirection:	Field
	streettype:			Field
	streetname:			Field
	streettypelong:		Field
	buildingnumber:		Field
	zipcode:			Field
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
		self.limit = 3

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
		from streetaddress.abbrevs import USA_ABBREVS
		abrevs = {v: k for k, v in USA_ABBREVS.items()}
		query = dict(zip(
			["buildingnumber", "streetdirection", "streetname", "streettype", "city", "state", "zipcode", "streettypelong"],
			[building, direction, streetname, streettype, city, state, zipcode, abrevs[streettype]]
		))
		streetTypeLong = {"st": "Street", "ln": "lane"}
		query["address"] = ""
		self.lookup(query)

	def name_lookup(self, first, middle, last):
		query = dict(zip(["firstname", "middlename", "lastname"], [first, middle, last]))
		for x in query.copy():
			if query[x] == "":
				del query[x]
		self.lookup(query)

	def phone_lookup(self, number):
		query = {"phone": number}
		self.lookup(query)

	def convert(self, value, options:FieldOptions, data:dict):
		if options.upper: value = str(value).upper()
		if options.lower: value = str(value).lower()
		if options.title: value = str(value).title()
		if options.space_to_underscore: value = str(value).replace(" ", "_")
		if options.exclude_symbols:
			for x in ["-", "(", ")", "+", "=", "|"]: value = str(value).replace(x, "")
		if options.remove_spaces: value = str(value).replace(" ", "")
		if options.formatphone != None:
			newphone = ""
			curr_index = 0
			for x in options.formatphone:
				if x == "x" and len(value)-1 >= curr_index:
					x = value[curr_index]
					curr_index += 1
				newphone += str(x)
			value = newphone
		if options.formatstr != None:
			value = options.formatstr
			for k, x in data.items():
				if type(x) == str:
					value = value.replace("{" + k + "}", x)
		if options.textsearch:
			return {"$text": {"$search": value}}
		return value


	def db_exists(self, collection):
		if self.CLIENT.get_database(collection.DB) == None:
			print("Database does not exist!")
			return False
		elif collection.COLL not in self.CLIENT[collection.DB].collection_names():
			print("Collection does not exist!")
			return False
		return True

	def get_all_queries(self, q, qvariants):
		#q = the parameters that WILL NOT change
		#qvariants = k: value to search, v: keys that can be used
		#example qvariants: 	{"john": ["FIRSTNAME", "ALIAS"]}
		allq = []
		for x in qvariants:
			for k in qvariants[x]:
				newq = q.copy()
				newq[k] = x
				if len(newq) > 0:
					allq.append(newq)
		if len(allq) == 0:
			allq.append(q)
		return allq
			

	def lookup(self, parameters):
		for k, p in parameters.copy().items():
			if k not in ["address"]:
				if p == None or p == "":
					del parameters[k]
		results = []
		for collection in self.collections:
			print("Searching through", collection.Description)
			qvariants = {} #key = the value we search for, value = the keys we can use
			q = {}
			for k, v in parameters.items():
				if k in collection.Fields:
					converted = self.convert(v, collection.Fields[k].options, parameters)
					if type(converted) == dict:
						q = converted
						break
					if converted != "":
						if collection.Fields[k].key != None:
							q[collection.Fields[k].key] = converted
						elif collection.Fields[k].keys != None:
							qvariants[v] = collection.Fields[k].keys.copy()
			queries = self.get_all_queries(q, qvariants)
			for query in queries:
				if len(query) == 0: continue
				print("Query:", query)
				if self.db_exists(collection) == False: continue
				qresults = list(self.CLIENT[collection.DB][collection.COLL].find(query).limit(self.limit))
				if len(qresults) > 0:
					print("Found something! ")
					results.append({"DB": collection.DB, "COLL": collection.COLL, "DESC": collection.Description, "query": query, "data": qresults})
		
		utils.save_json("lookup.json", results)
		return results
			

	
					