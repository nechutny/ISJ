import sys
import re

class arguments:
	filename = False;
	name = False;
	lang = "cze,eng";
	url = False;
	downloaded = False;
	keep = False;

	def __init__(self, args):
		i = 1;
		try:
			while i < len(args) :
				if args[i] == "-f":
					self.filename = args[i+1]
					i += 1;
				elif args[i] == "-l":
					self.lang = args[i+1].lower();
					if re.match(r"^([a-z]{3},[a-z]{3})$",self.lang) == None:
						print >> sys.stderr, "Zadane jazyky nemaji spravny format: abc,xyz";
						sys.exit(1);
					i += 1;
				elif args[i] == "-u":
					self.lang = args[i+1];
					i += 1;
				elif args[i] == "-n":
					self.name = args[i+1];
					i += 1;
				elif args[i] == "--downloaded":
					self.downloaded = True;
				elif args[i] == "--keep":
					self.keep = True;
				elif re.match(r"http\:\/\/www\.opensubtitles.com/[a-z]{2}/subtitles/([0-9]+)/(.*)",args[i]) != None:
					self.url = args[i]+"/xml";
				else:
					print >> sys.stderr, "Neznamy argument "+args[i];
					sys.exit(1);

				i += 1;
		except IndexError:
			print >> sys.stderr, "Spatne argumenty.";
			sys.exit(1);

