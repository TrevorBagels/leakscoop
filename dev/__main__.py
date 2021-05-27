from . import utils
from . import lookups
import argparse, sys, os

import time

m = lookups.Lookups()

for p in ["./results", "./collections"]:
	if os.path.exists(p) == False:
		os.mkdir(p)



if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	search_options = ["NAME", "ADDRESS", "PHONE", "EMAIL", "VRN", "AUTO"]
	ap.add_argument("--search", default="AUTO", help="What to search with. Options currently are: " + ", ".join(search_options))
	ap.add_argument("--firstname", default=None, help="First name. Don't use this without also providing --lastname.")
	ap.add_argument("--middlename", default=None, help="Middle name.")
	ap.add_argument("--lastname", default=None, help="Last name.")
	ap.add_argument("--phone", default=None, help="Phone number.")
	ap.add_argument("--email", default=None, help="Email address.")
	ap.add_argument("--VRN", default=None, help="Vehicle registration number / license plate.")
	ap.add_argument("--limit", default=2, help="How many documents to return per query. Default = 2")
	ap.add_argument("--address", default=None, help="Address. ")
	filternames = []
	for c in m.collections:
		for f in c.Filter:
			if f not in filternames:
				filternames.append(f)
	for x in filternames:
		ap.add_argument(f"--{x}", default=None, help="For additional filtering.")



	args = ap.parse_args()
	m.args = args.__dict__
	m.limit = args.limit
	if args.search.upper() not in search_options:
		print("Invallid search mode. Select one of the following:",", ".join(search_options))
		sys.exit()
	


	searchmode = args.search.upper()
	if searchmode == "AUTO":
		search_fields = {
			"NAME": ["firstname", "middlename", "lastname"],
			"ADDRESS": ["address"],
			"PHONE": ["phone"],
			"EMAIL": ["email"],
			"VRN": ["VRN"]
		}
		mode = None
		for k, v in args.__dict__.items():
			if k == "search": continue
			if v != None:
				for k1, v1 in search_fields.items():
					if k in v1:
						mode = k1
		if mode != None:
			searchmode = mode.upper()


	print("MODE:", searchmode)

	if searchmode == "NAME":
		m.name_lookup(args.firstname, args.middlename, args.lastname)
	elif searchmode == "ADDRESS":
		from address_parser import Parser
		adp = Parser()
		addy = adp.parse(args.address)
		args = [addy.number.tnumber, addy.road.direction, addy.road.name, addy.road.suffix, addy.locality.city, addy.locality.state, addy.locality.zip]
		m.address_lookup(*args)
	elif searchmode == "PHONE":		
		m.phone_lookup(args.phone)
	elif searchmode == "EMAIL":
		m.email_lookup(args.email)
	elif searchmode == "VRN":
		m.plate_lookup(args.VRN)
		
		

