auth_token = 'S=s1:U=72a0c:E=14790c4cc95:C=1403913a098:P=1cd:A=en-devtoken:V=2:H=62d96bedf9a1adbb47b43c67b1474b95'

sandbox = False

consumer_key = 'liushuaikobe'
consumer_secret = 'be4517542c7860ca'

def get_evernote_host(international=False, sandbox=False):
	if sandbox:
		return 'sandbox.evernote.com'
	else:
		if international:
			return  'www.evernote.com'
		else:
			return 'app.yinxiang.com'

enml_legal_tag = [ \
			'a',\
			'abbr', \
			'acronym', \
			'address', \
			'area', \
			'b,', \
			'bdo', \
			'big', \
			'blockquote', \
			'br', \
			'caption', \
			'center', \
			'cite', \
			'code', \
			'col', \
			'colgroup', \
			'dd', \
			'del', \
			'dfn', \
			'div', \
			'dl', \
			'dt', \
			'em', \
			'font', \
			'h1', \
			'h2', \
			'h3', \
			'h4', \
			'h5', \
			'h6', \
			'hr', \
			'i', \
			'img', \
			'ins', \
			'kbd', \
			'li', \
			'map', \
			'ol', \
			'p', \
			'pre', \
			'q', \
			's', \
			'samp', \
			'small', \
			'span', \
			'strike', \
			'strong', \
			'sub', \
			'sup', \
			'table', \
			'tbody', \
			'td', \
			'tfoot', \
			'th', \
			'thead', \
			'title', \
			'tr', \
			'tt', \
			'u', \
			'ul', \
			'var', \
			'xmp'
			]

enml_ilegal_attr = [ \
			'id', \
			'class', \
			'onclick', \
			'ondblclick', \
			'accesskey', \
			'data', \
			'dynsrc', \
			'tabindex'
			]