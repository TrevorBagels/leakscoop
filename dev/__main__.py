from . import main
import argparse, sys



m = main.Main()


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	search_options = ["NAME", "ADDRESS"]
	ap.add_argument("--search", default="NAME", help="What to search with. Options currently are: " + ", ".join(search_options))
	ap.add_argument("--firstname", default=None, help="First name. Don't use this without also providing --lastname.")
	ap.add_argument("--middlename", default=None, help="Middle name.")
	ap.add_argument("--lastname", default=None, help="Last name.")
	ap.add_argument("--phone", default=None, help="Phone number in the format of +xx (xxx) xxx xxxx")

	ap.add_argument("--address", default=None, help="Address. ")
	
	args = ap.parse_args()

	if args.search.upper() not in search_options:
		print("Invallid search mode. Select one of the following:",", ".join(search_options))
		sys.exit()

	searchmode = args.search.upper()

	if searchmode == "NAME":
		m.name_lookup(args.firstname, args.middlename, args.lastname)
	elif searchmode == "ADDRESS":
		from address_parser import Parser
		adp = Parser()
		addy = adp.parse(args.address)
		args = [addy.number.tnumber, addy.road.direction, addy.road.name, addy.road.suffix, addy.locality.city, addy.locality.state, addy.locality.zip]
		m.address_lookup(*args)
	elif searchmode == "PHONE":
		import phonenumbers
		phone = args.phone
		parsed = phonenumbers.parse(phone)
		parsed = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
		
		

