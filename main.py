import os

from client import NoteblockClient

if __name__ == '__main__':
    client = NoteblockClient()
    client.run(os.environ['NOTEBLOCK_SECRET'])
