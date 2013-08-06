import sys
import markdown
import HTMLParser

import config

def read_markdown_from_file(path):
	return open(path, 'r').read()

def md2html(md):
	return markdown.markdown(md).encode("utf-8")

def html2enml(html):
	enmlParser = EnmlParser(config.enml_legal_tag, config.enml_ilegal_attr)
	enmlParser.feed(html)
	# print enmlParser.get_clean_text()
	return enmlParser.get_clean_text()


class EnmlParser(HTMLParser.HTMLParser):
	'''
	ENML tags & attributes filter.
	'''
	def __init__(self, legal_tag, ilegal_attr):
		HTMLParser.HTMLParser.__init__(self)
		self.legal_tag = legal_tag
		self.illegal_attr = ilegal_attr
		self.clean_text = []
		self.pre_tag = None

	def handle_starttag(self, tag, attrs):
		if tag == 'body':
			self.pre_tag = self.legal_tag[0] # make the pre_tag be a legle tag on purpose
			return
		if tag in self.legal_tag:
			self.clean_text.append('<')
			self.clean_text.append(tag)
			for name, val in attrs:
				if name not in self.illegal_attr and not name.startswith('on'):
					exp = ' %s="%s"' % (name, val)
					self.clean_text.append(exp)
			self.clean_text.append('>')
		self.pre_tag = tag 

	def handle_data(self, data):
		if self.pre_tag in self.legal_tag:
			self.clean_text.append(data)

	def handle_endtag(self, tag):
		if tag in self.legal_tag:
			self.clean_text.append('</{0}>'.format(tag))
		self.pre_tag = None

	def get_clean_text(self):
		return self.wrapENML(''.join(self.clean_text))

	def handle_media(self):
		'''
		Do something specially for the media resource(tag and attributes) in html.
		But actually I found that these tags without any extra handling works perfectly in evernote!
		notice -> there are 3 protocols that enml supporting : http, https, file
		'''
		pass

	def wrapENML(self, clean_text):
		header = '<?xml version="1.0" encoding="UTF-8"?>\n'
		header += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n'
		return '%s\n<en-note>%s</en-note>' % (header, clean_text)

def get_default_notetitle(path):
	'''
	Suppose we are in *nix OS.:)
	'''
	separator = '/'
	return path.split(separator)[-1].split('.')[0]

def import_evernote_lib():
	lib_path = './lib'
	if lib_path not in sys.path:
		sys.path.append(lib_path)












		