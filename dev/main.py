
from threading import current_thread
from typing import ForwardRef
import datetime
import colorama
from pymongo.message import query
from . import utils
from .prodict import Prodict
import colorama

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
	
class Filter(Prodict):
	value:			list
	casesensitive:	bool
	logic:			bool

	def init(self):
		self.value = []
		self.casesensitive = False
		self.logic = True

class Collection(Prodict):
	DB:				str
	COLL:			str
	Description:	str
	Options:		FieldOptions
	Fields:			dict[str, Field]
	Filter:		dict[str, Filter]


import pymongo, os


class Main:
	def __init__(self):
		self.limit = 3
		self.CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
		self.collections:list[Collection] = []
		self.get_collection_config()
		self.args:dict[str, str] = {}
		self.lookuptype = "NAME"
		
	def load_collection(self, x):
		if "Fields" not in x:
			print(colorama.ansi.Fore.RED, f"Collection has no fields!")
		if "Filter" not in x:
			x["Filter"] = {}
		for fname, field in x["Fields"].items():
			if type(field) == str:
				x["Fields"][fname] = Field()
				x["Fields"][fname].key = field
				continue
		for fname, filt in x["Filter"].items():
			if "values" in filt:
				filt["value"] = filt["values"]
			del filt["values"]
		return Collection.from_dict(x)

	def get_collection_config(self):
		for f in os.listdir("./collections"):
			if f.endswith(".json"):
				c = [self.load_collection(x) for x in utils.load_json(f"./collections/{f}")]
				self.collections = self.collections + c
		#set options and things
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

	def convert(self, value, options:FieldOptions, data:dict):
		if options.upper: value = str(value).upper()
		if options.lower: value = str(value).lower()
		if options.title: value = str(value).title()
		if options.space_to_underscore: value = str(value).replace(" ", "_")
		if options.exclude_symbols:
			for x in ["-", "(", ")", "+", "=", "|"]: value = str(value).replace(x, "")
		if options.remove_spaces: value = str(value).replace(" ", "")
		if options.formatphone != None:
			newphone = []
			currphone = list(value)
			curr_index = 0
			for x in options.formatphone:
				newphone.append(x)
				if x == "x":
					newphone[len(newphone)-1] = currphone[0]
					currphone.pop(0)
			value = "".join(newphone)
		
		if options.formatstr != None:
			value = options.formatstr
			for k, x in data.items():
				if type(x) == str:
					value = value.replace("{" + k + "}", x)
		if options.textsearch:
			return {"$text": {"$search": value}}
		return value


	def db_exists(self, collection):
		#return False #uncomment this line for testing (when you wanna just see the queries without actually interacting with the database)
		if self.CLIENT.get_database(collection.DB) == None:
			print(colorama.ansi.Fore.RED, "Database does not exist!")
			return False
		elif collection.COLL not in self.CLIENT[collection.DB].collection_names():
			print(colorama.ansi.Fore.RED, "Collection does not exist!")
			return False
		return True

	def can_use_collection(self, collection:Collection, parameters):
		blocked = False
		for k, f in collection.Filter.items():
			if k not in self.args:
				self.args[k] = None
			value = self.args[k] in f.value
			if (value == f.logic) == False:
				blocked = True
				break
		return not blocked

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
		parameters_original = parameters.copy()
		starttime = datetime.datetime.now()
		for k, p in parameters.copy().items():
			if k not in ["address"]:
				if p == None or p == "":
					del parameters[k]
		results = []
		for collection in self.collections:
			print(colorama.ansi.Fore.WHITE, "Searching through", colorama.ansi.Fore.LIGHTMAGENTA_EX, collection.Description)
			if self.can_use_collection(collection, parameters) == False:
				print(colorama.ansi.Fore.WHITE, "Skipping collection because of filters in place!")
				continue
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
						elif collection.Fields[k].keylist != None:
							qvariants[converted] = collection.Fields[k].keylist.copy()
			queries = self.get_all_queries(q, qvariants)
			for query in queries:
				if len(query) == 0: continue
				print(colorama.ansi.Fore.WHITE, "Query:", colorama.ansi.Fore.BLUE, query)
				if self.db_exists(collection) == False: continue
				qresults = list(self.CLIENT[collection.DB][collection.COLL].find(query).limit(self.limit))
				if len(qresults) > 0:
					print(colorama.ansi.Fore.LIGHTCYAN_EX, "Found something! ")
					for res in qresults:
						self.print_result(collection, res, parameters_original)
					results.append({"DB": collection.DB, "COLL": collection.COLL, "DESC": collection.Description, "query": query, "data": qresults})
					utils.save_json(f"results/latest.json", qresults)
		timestamp = datetime.datetime.now().strftime("%m-%d-%y_%H:%M:%S")
		finalresults = {"started": starttime.strftime("%m-%d-%y_%H:%M:%S"), "ended": timestamp, "parameters": parameters_original, "results": results}
		utils.save_json(f"results/{timestamp}_results.json", finalresults)
		return results
	
	def table_line(self, stuff:list, spacing=25):
		txt = ""
		for x in stuff:
			txt += x + (" " * (spacing-len(x)))
		return txt


	def print_result(self, collection:Collection, result, parameters):
		for fn, f in collection.Fields.items():
			if fn not in parameters or parameters[fn] not in ["", None]: #we don't know this parameter
				keys = []
				if f.key != None:keys.append(f.key)
				elif f.keylist != None: keys = f.keylist
				for key in keys:
					if key != None and key in result and result[key] not in [None, ""]:
						print(colorama.ansi.Fore.GREEN, self.table_line([fn, result[key], f"({key})"]))
