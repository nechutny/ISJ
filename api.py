import urllib2;
import sys;
from xml.dom import minidom
import xml.parsers.expat
import struct
import os
import re

class api:

	_tmp = {};

	def subtitlesByLink(self, url):
		try:
			http = urllib2.urlopen(url);
		except urllib2.URLError:
			print >> sys.stderr, "Chyba pri pripojovani k serveru. Mate pripojeni?. "
			sys.exit(1);

		data = http.read();


		res = [];
		try:
			dom = minidom.parseString(data);
		except xml.parsers.expat.ExpatError:
			print >> sys.stderr, "Nactena data z api nejsou validni XML. "
			sys.exit(1);
		results = dom.getElementsByTagName('subtitle');
		for result in results:
				if len(result.getElementsByTagName("MovieName")) > 0 and not self.isDownloaded( re.findall(r'-([a-z]{3})$',result.getElementsByTagName("ISO639")[0].getAttribute("LinkSearch"))[0] ):
					res.append( [
						result.getElementsByTagName("IDSubtitle")[0].getAttribute("LinkDownload"),
						#"http://www.opensubtitles.org/en/subtitleserve/sub/"+result.getElementsByTagName("IDSubtitle")[0].firstChild.data,
						"http://www.opensubtitles.org"+result.getElementsByTagName("IDSubtitle")[0].getAttribute("Link"),
						re.findall(r'-([a-z]{3})$',result.getElementsByTagName("ISO639")[0].getAttribute("LinkSearch"))[0],
						result.getElementsByTagName("IDSubtitle")[0].firstChild.data
						]);

		return res;

	def isDownloaded(self,lang):
		try:
			if self._tmp[lang] == 1:
				return True
			else:
				self._tmp[lang] = 1
				return False
		except KeyError:
			self._tmp[lang] = 1
			return False;

	def downloadSubtitle(self, data):
		if not os.path.exists("./download"):
			os.makedirs("./download");
		if not os.path.exists("./download/"+data[2] ):
			os.makedirs("./download/"+data[2] );

		#http://www.opensubtitles.org/en/subtitleserve/sub/3621574

		subs = urllib2.urlopen(data[0]);
		if subs.headers.get("Content-type") == "text/html":
			print >> sys.stderr, "Vycerpan limit stazeni -> je pozadovan opis captcha. Nemohu pokracovat. Muzete spustit aplikaci alespon s casti stazenych titulku prostrednictvim --downloaded"
			sys.exit(1);

		output = open("./download/"+data[2]+"/"+data[3]+".zip",'wb');
		output.write(subs.read());
		output.close();

	def searchByFile(self, filename, lang):
		hash = self.__hashFile(filename);

		return "http://www.opensubtitles.org/en/search/sublanguageid-"+lang+"/moviehash-"+hash+"/xml"

	def searchByName(self, name, lang ):

		# prepare url
		name = name.replace(" ","%20");
		myurl = "http://www.opensubtitles.org/en/search2/sublanguageid-"+lang+"/moviename-"+name+"/xml";

		return self.__fetchData(myurl);

	def searchBySubs(self, url, lang):
		try:
			http = urllib2.urlopen(url);
		except urllib2.URLError:
			print >> sys.stderr, "Chyba pri pripojovani k serveru. Mate pripojeni?. "
			sys.exit(1);
		data = http.read();
		dom = minidom.parseString(data);

		id = re.findall(r".*\/([0-9]+)\/.*",url)[0];

		res = [ ["http://dl.opensubtitles.org/en/download/subad/"+id, url, dom.getElementsByTagName("LanguageName")[0].getAttribute("SubLanguageID"), id] ]
		
		x = re.sub(r"sublanguageid-([a-z]{3})","sublanguageid-"+lang, "http://www.opensubtitles.org"+dom.getElementsByTagName("MovieName")[0].getAttribute("Link"))+"/xml";
		
		x = self.subtitlesByLink(x);

		for y in x:
			res.append(y);

		return res;
		
	def __fetchData(self, myurl):
		url = "";
		# search
		try:
			http = urllib2.urlopen(myurl);
		except urllib2.URLError:
			print >> sys.stderr, "Chyba pri pripojovani k serveru. Mate pripojeni?. "
			sys.exit(1);

		# if found only one movie, then it redirect so check urls
		if str(http.geturl()) != str(myurl):
			url = http.geturl()+"/xml";
		else:
			data = http.read();
			#print data;
			#parse xml
			url = self.__parseResult(data);
		return url;

	def __parseResult(self, data):
		try:
			dom = minidom.parseString(data);
		except xml.parsers.expat.ExpatError:
			print >> sys.stderr, "Nactena data z api nejsou validni XML. "
			sys.exit(1);
		results = dom.getElementsByTagName('subtitle');

		

		# more movies so user must chose
		if len(results) > 1:
			print("Bylo nalezeno vice filmu s timto nazvem/hashem, zvolte o jaky se jedna.");
			i = 1;
			for result in results:
				if len(result.getElementsByTagName("MovieName")) > 0:
					print str(i)+") "+result.getElementsByTagName("MovieName")[0].firstChild.data+" ("+result.getElementsByTagName("MovieYear")[0].firstChild.data+") - Titulku: "+ (result.getElementsByTagName("TotalSubs")[0].firstChild.data if len(result.getElementsByTagName("TotalSubs")) > 0 else "???");
					i += 1;

			n = 0;
			while( n < 1 or n > i ):
				print "Zadejte cislo, ktery film zvolit: ";
				try:
					n = raw_input();
				except EOFError:
					print >> sys.stderr, "Ukoncen vstup bez zvoleni filmu, takze koncim. "
					sys.exit(0);
				try:
					n = int(n,10);
				except ValueError:
					n = 0;
			i = 1;
			for result in results:
				if len(result.getElementsByTagName("MovieName")) > 0:
					if i == n:
						url = "http://www.opensubtitles.org"+result.getElementsByTagName("MovieID")[0].getAttribute("Link");
						break;
					i += 1;
		return url;

	# googled function for calculating movie hash
	# http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes#Python
	def __hashFile(self, name):
		try:

			longlongformat = 'q'  # long long
			bytesize = struct.calcsize(longlongformat)

			f = open(name, "rb") 

			filesize = os.path.getsize(name)
			hash = filesize

			if filesize < 65536 * 2:
				return "SizeError"

			for x in range(65536/bytesize):
				buffer = f.read(bytesize)
				(l_value,)= struct.unpack(longlongformat, buffer)
				hash += l_value
				hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number


			f.seek(max(0,filesize-65536),0)
			for x in range(65536/bytesize):
				buffer = f.read(bytesize)
				(l_value,)= struct.unpack(longlongformat, buffer)
				hash += l_value
				hash = hash & 0xFFFFFFFFFFFFFFFF

			f.close()
			returnedhash =  "%016x" % hash
			return returnedhash

		except(IOError):
			return "IOError"
