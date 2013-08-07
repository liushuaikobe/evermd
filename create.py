import sys

import config
import utils
utils.import_evernote_lib()
from oauth import EvermdAuth

from evernote.api.client import EvernoteClient
import lib.evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import lib.thrift.protocol.TBinaryProtocol as TBinaryProtocol
import lib.thrift.transport.THttpClient as THttpClient

class Evermd(object):
	'''
	Main Class 
	'''
	notestore = None
	evermdAuth = None
	noteStoreUrl = None
	authToken = None

	def __init__(self):
		self.evermdAuth = EvermdAuth()

	def auth(self):
		if not self.noteStoreUrl or not self.authToken:
			self.noteStoreUrl = self.evermdAuth.getNoteStoreUrl()
			self.authToken = self.evermdAuth.getToken()


	def get_notestore(self):
		if self.notestore:
			return self.notestore

		noteStoreHttpClient = THttpClient.THttpClient(self.noteStoreUrl)
		noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
		self.noteStore = NoteStore.Client(noteStoreProtocol)

		return self.noteStore

	def fetch_notebook_list(self):
		print 'Start fetching your notebook list...'
		notebooks = self.get_notestore().listNotebooks(self.authToken)
		return notebooks

	def create(self, title, content, notebook=None):
		note = Types.Note()

		note.title = title
		note.content = content
		if notebook:
			note.notebookGuid = notebook.guid

		created_note = self.get_notestore().createNote(self.authToken, note)
		print 'Successfully created a note with GUID: ', created_note.guid

	def test(self):
		pass

def main():
	if len(sys.argv) < 2:
		print 'Give the correct path of the markdown file.'
		return

	evermd = Evermd()

	evermd.auth()

	notebooks = evermd.fetch_notebook_list()
	for i in range(len(notebooks)):
		print i, ".", notebooks[i].name

	index = raw_input('Give me the notebook index you want to create note in (None means default notebook): ')
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

	title = raw_input('Input the tile of the note (None means the same as the name of markdown file): ')
	if not title:
		title = utils.get_default_notetitle(md_file_path)
	print 'Trying to create a note...'
	evermd.create(title, enml, notebook)

if __name__ == '__main__':
	main()
	
		
