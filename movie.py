import urllib2;	# http
import re; 		# regexp
import os;		# os

class movie:
	sizes = [];
	movie_files = [];
	subtitle_files = [];
	link = "";
	name = "";
	id = 0;
	lang = "";
	download_link = "";
	all_subtitles = [];


	def __init__(self,link):
		self.link = link;
		self.parse();


	def parse(self):
		# download page
		request = urllib2.Request(self.link);
		handler = urllib2.urlopen(request);
		html =  handler.read();

		# regexp data
		self.sizes			= re.findall(r'\>(\d+)\<\/a',html);
		self.name			= re.findall(r'LoadVideoBar\(\"(.*)\"\)\;',html)[0];
		self.movie_files	= re.findall(r'verze\"\s\/\>(.*)\<\/a\>',html);
		self.subtitle_files	= re.findall(r'titulky\"\s\/\>(.*)\.srt|sub\n',html);
		self.all_subtitles	= re.findall(r'href\=\"\/cs\/subtitles\/([0-9]{1,})\/',html);
		self.id				= re.findall(r'/(\d{1,})/',self.link)[0];
		self.lang			= re.findall(r'sublanguageid\-(...)/idmovie',html)[0];
		self.download_link	= "http://dl.opensubtitles.org/cs/download/subb/"+self.id;


	def download(self):
		if self.download_link == "":
			self.parse();


		if not os.path.exists("./download"):
			os.makedirs("./download");
		if not os.path.exists("./download/"+self.lang ):
			os.makedirs("./download/"+self.lang );

		subs = urllib2.urlopen(self.download_link)
		output = open("./download/"+self.lang+"/"+self.id,'wb')
		output.write(subs.read())
		output.close()





	def debug(self):
		print "ID: "+self.id;
		print "Name: "+self.name;
		print "Link: "+self.link;
		print "Download: "+self.download_link;
		print "Lang: "+self.lang;
		print "Sizes: ";
		print self.sizes;
		print "Movie files: ";
		print self.movie_files;
		print "Subtitle files: ";
		print self.subtitle_files;
		print "All subtitles: ";
		print self.all_subtitles;
