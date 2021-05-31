from pymongo import client_options
from . import main




class Lookups(main.Main):
	def __init__(self):
		super().__init__()

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
		import phonenumbers
		if "+" not in number:
			number = "+1 " + number 
		parsed = phonenumbers.parse(number)
		parsed = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)[-10:]
		query = {"phone": parsed}
		self.lookup(query)
	def email_lookup(self, email):
		query = {"email": email}
		self.lookup(query)
	def plate_lookup(self, vrn):
		query = {"vrn": vrn}
		self.lookup(query)