import sys
sys.path.append('./lib')

import utils
import config

from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types

def create(title, content, note_store, notebook=None):
	note = Types.Note()

	note.title = title
	note.content = content
	if notebook:
		note.notebookGuid = notebook.guid

	created_note = note_store.createNote(note)
	print 'Successfully created a note with GUID: ', created_note.guid

def main():
	if len(sys.argv) < 2:
		print 'Give the correct path of the markdown file.'
		return

	client = EvernoteClient(token=config.auth_token, sandbox=config.sandbox)
	print 'Start verifying your id...'
	note_store = client.get_note_store()
	print 'Verify successfully! Start fetching your notebook list...'
	notebooks = note_store.listNotebooks()

	for i in range(len(notebooks)):
		print i, ".", notebooks[i].name
	index = raw_input('Give me the notebook index you want to create note in(None means default notebook): ')
	try:
		index = int(index)
		if index not in range(len(notebooks)):
			raise Exception()
		notebook = notebooks[index]
	except Exception, e:
		print 'Index Error, will use default notebook.'
		notebook = None

	md_file_path = sys.argv[1]
	md = unicode(utils.read_markdown_from_file(md_file_path), 'utf-8')
	html = utils.md2html(md)
	enml = utils.html2enml(html)

	title = raw_input('Input the tile of the note(None means the same as the name of markdown file):')
	if not title:
		title = utils.get_default_notetitle(md_file_path)
	print 'Trying to create a note...'
	create(title, enml, note_store, notebook)

if __name__ == '__main__':
	main()
	
		
