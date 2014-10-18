import zipfile
import os
import re
import sys
import chardet

class subtitle:
	zip_name = "";
	id = 0;
	lang = "";
	sub_file = "";
	data = [];

	def __init__(self, id, lang):
		self.zip_name = "./download/"+lang+"/"+id+".zip";
		self.id = id;
		self.lang = lang;
		self.data = [];


	def compare(self, comp):
		self.parse();
		comp.parse();
		i = 0;

		fix1 = 0;
		fix2 = 0;

		timediff = 0;

		while len(self.data) > i or len(comp.data) > i:
			x1 = self.get(i+fix2);
			x2 = comp.get(i+fix1);

			k = 0;
			tmp1 = x2[0].count("!");
			tmp2 = x2[0].count("?")
			#tmp3 = x2[0].count("-")
			while(k < 7 and (tmp1 > 0 or tmp2 > 0)):# or tmp3 > 0) ):
				counted = False
				if tmp1 > 0:
					if self.get(i+fix2+k)[0].count("!") > 0:
						break;
					else:
						print(self.get(i+fix2+k)[0]+"\t");
						counted = True
						k += 1;
				if tmp2 > 0:
					if self.get(i+fix2+k)[0].count("?") > 0:
						break;
					else:
						if not counted:
							print(self.get(i+fix2+k)[0]+"\t");
							k += 1;
							counted = True;
				#if tmp3 > 0:
				#	if self.get(i+fix2+k)[0].count("-") > 0:
				#		break;
				#	else:
				#		if not counted:
				#			print("a"+str( self.get(i+fix2+k)[1])+"s -> "+str( self.get(i+fix2+k)[2])+"s: "+ self.get(i+fix2+k)[0]);
				#			k += 1;
				#			counted = True;

			fix2 += k;
			x1 = self.get(i+fix2);
			


			j = 0;
			tmp1 = x1[0].count("!");
			tmp2 = x1[0].count("?")
			#tmp3 = x1[0].count("?")
			while(j < 7 and (tmp1 > 0 or tmp2 > 0 )):#or tmp3 > 0) ):
				counted = False
				if tmp1 > 0:
					if comp.get(i+fix1+j)[0].count("!") > 0:
						timediff = self.get(i+fix2+k)[1]-x2[1]
						break;
					else:
						print("\t"+comp.get(i+fix1+j)[0]);
						j += 1;
						counted = True;
				if tmp2 > 0:
					if comp.get(i+fix1+j)[0].count("?") > 0:
						timediff = self.get(i+fix2+k)[1]-x2[1]
						break;
					else:
						if not counted:
							j += 1;
							print("\t"+ comp.get(i+fix1+j)[0]);
							counted = True;
				#if tmp3 > 0:
				#	if comp.get(i+fix1+j)[0].count("-") > 0:
				#		break;
				#	else:
				#		if not counted:
				#			j += 1;
				#			print("b\t"+str( comp.get(i+fix1+j)[1])+"s -> "+str( comp.get(i+fix1+j)[2])+"s: "+ comp.get(i+fix1+j)[0]);
				#			counted = True;

			fix1 += j;
			x2 = comp.get(i+fix1);

			if x2[1]-x1[1] > 20+timediff and x1[0] != "":
				print(x1[0]+"\t");
				fix2 += 1;
				x1 = self.get(i+fix2);
			if x1[1]-x2[1] > 20 and x2[0] != "":
				print("\t"+x2[0]);
				fix1 += 1;
				x2 = comp.get(i+fix1);

			print(x1[0]+"\t"+x2[0]);
			
			i += 1;
			if x1[0] == x2[0] == "" and x1[2] == x2[2] == 0:
				break

		return self;

	def delete(self):
		os.unlink("./download/"+self.lang+"/"+self.id+".zip");
		os.unlink(self.sub_file);

	def debug(self):
		print self.zip_name;
		print self.sub_file;
		print self.lang;
		print self.id;
		print self.data;

	def get(self, index):
		if len(self.data) == 0:
			self.__parse_subs();
		try:
			return self.data[index];
		except IndexError:
			return ["",0,0];

	def parse(self):
		self.__parse_subs();

	def __parse_subs(self):
		if self.sub_file == "":
			print  >> sys.stderr, "Neni soubor, ktery by se mel parsovat "+self.id;
		if len(self.data) > 0:
			return True;


		
		file = open(self.sub_file).read();

		#print "Data: "+file;

		# Idiots are not using utf-8....
		x = chardet.detect(file[0:300]);
		file = file.decode(x['encoding']);

		if self.sub_file[-3:-1] == "sr":
			self.__parse_subs_srt(file);
		else:
			self.__parse_subs_sub(file);

		return self;

	def __parse_subs_srt(self,datas):
		#print datas;
		

		splits = [s.strip() for s in re.split(r'\n\s*\n', datas) if s.strip()]
		regex = re.compile(r'''(?P<index>\d+).*?(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})\s*.*?\s*(?P<text>.*)''', re.DOTALL)
		for s in splits:
			try:
				r = regex.findall(s)
				times1 = map(int, re.split(r"[:,]", r[0][1]));
				times2 = map(int, re.split(r"[:,]", r[0][2]));
				self.data.append([ r[0][3].replace('\n', '| ').replace('\r',''), times1[0]*3600+times1[1]*60+times1[2]+times1[3]/1000, times2[0]*3600+times2[1]*60+times2[2]+times2[3]/1000]);
			except IndexError:
				True
		return self;


	def __parse_subs_sub(self,datas):
		regex = re.compile(r'^\{([0-9]{1,})\}\{([0-9]{1,})\}(.*)$');
		for line in datas.splitlines():
			x = regex.findall(line)[0];
			self.data.append([x[2], int(x[0],10)/25, int(x[1],10)/25 ]);
		return self;


	def unzip(self):
		try:
			with zipfile.ZipFile(self.zip_name) as zf:
				for member in zf.infolist():
					words = member.filename.split('/')
					path = "./"
					for word in words[:-1]:
						drive, word = os.path.splitdrive(word);
						head, word = os.path.split(word);
						if word in (os.curdir, os.pardir, ''): continue
						path = os.path.join(path, word);

					if re.match(r".*[.](srt|sub)$",words[0]) != None:
						zf.extract(member, "./download/"+self.lang+"/");
						os.rename("./download/"+self.lang+"/"+words[0], "./download/"+self.lang+"/"+self.id+"."+(re.findall(r".*[.](srt|sub)$",words[0])[0]));
						self.sub_file = "./download/"+self.lang+"/"+self.id+"."+(re.findall(r".*[.](srt|sub)$",words[0])[0]);
						
		except zipfile.BadZipfile:
			print  >> sys.stderr, "Soubor "+self.zip_name+" neni validni zip";

		self.__parse_subs();


