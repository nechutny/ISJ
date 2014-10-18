'''/*
	*
	*	Name:		ISJ Project
	*	Author: 	Stanislav Nechutny - xnechu01
	*	Repository:	git@nechutny.net:vut.git/ISJ
	*	Revision:	1
	*	Created:	2014-02-25 22:09
	*	Modified:	2014-02-26 01:36
	*
	*	!!! I HATE PYTHON !!!
	*
	*	Run:
	*			[ -f movie_filename.avi ]
	*				Search for subtitles for this movie
	*
	*			[ -l LANG ]
	*				Subtitles languages, can be more separated cia comma: -l eng,czk,svk
	*
	*			[ -u URL ]
	*				Download subtitles from url
	*
	*			[ -n NAME]
	*				Search for movie with given name
	*
	*			[ --downloaded ]
	*				Don't download, use downloaded files
	*
	*			[ --keep ]
	*				Don't delete downloaded files
	*
	*/'''


import sys;
import os;
import re;
from arguments import arguments;
from api import api;
from subtitle import subtitle;
#from movie import movie

parameters = arguments(sys.argv);

api = api();
downloads = [];

if parameters.downloaded == False:
	if parameters.url != False:
		downloads = api.searchBySubs(parameters.url, parameters.lang);
	elif parameters.name != False :
		parameters.url = api.searchByName(parameters.name, parameters.lang);
		downloads = api.subtitlesByLink(parameters.url);
	elif parameters.filename != False:
		parameters.url = api.searchByFile(parameters.filename, parameters.lang);
		downloads = api.subtitlesByLink(parameters.url);

	#print parameters.url;

	
else:
	for lang in os.listdir("./download/"):
		for s in os.listdir("./download/"+lang+"/"):
			if re.match(r".*[.](zip)$",s) != None:
				downloads.append(["","",lang, re.findall(r'([0-9]{1,})',s)[0]]);
subs = [];

for download in downloads:
	if parameters.downloaded == False:
		api.downloadSubtitle(download);
	X = subtitle(download[3],download[2]);
	subs.append(X);



for i in range(0,len(subs)):
	subs[i].unzip();
	#subs[i].debug();

if len(subs) < 2:
	print  >> sys.stderr, "Nebylo nalezeno dostatek titulku pro porovnavani."
	sys.exit(1);

if subs[0].lang != arguments.lang[0:3]:
	subs[0], subs[1] = subs[1], subs[0];

subs[0].compare( subs[1] );

if not parameters.keep:
	subs[0].delete();
	subs[1].delete();



