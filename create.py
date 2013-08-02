import sys
sys.path.append('./lib')

import hashlib
import markdown

import utils

from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types


auth_token = 'S=s1:U=72a0c:E=14790c4cc95:C=1403913a098:P=1cd:A=en-devtoken:V=2:H=62d96bedf9a1adbb47b43c67b1474b95'

sandbox = True

def create(title, content, note_store):
	note = Types.Note()
	note.title = title
	note.content = content
	created_note = note_store.createNote(note)
	print 'Successfully created a note with GUID: ', created_note.guid

def main():
	if len(sys.argv) < 2:
		print 'markdown file not available.'
		return
	client = EvernoteClient(token=auth_token, sandbox=sandbox)
	note_store = client.get_note_store()
	notebooks = note_store.listNotebooks()
	for notebook in notebooks:
		print "-> ", notebook.name
	md_file_path = sys.argv[1]
	title = raw_input('input the tile of the note:')
	html = utils.md2html(unicode(utils.read_markdown_from_file(md_file_path), 'utf-8'))
	create(title, utils.html2enml(html), note_store)

if __name__ == '__main__':
	main()
	
		
