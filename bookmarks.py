#!/home/linuxbrew/.linuxbrew/bin/python3.7

import os
import sqlite3
import sys
from dataclasses import dataclass
import json
from base64 import b64encode
import random
from typing import Iterable
import argparse

# This is for WSL; you might need a different path
DATABASE_FNAME = '/mnt/c/Users/arvensis/AppData/Local/Google/Chrome/User Data/Default/Web Data'
SEARCH_ENGINES_TABLE = 'keywords'

def firefox_guid() -> str:
    """
    Firefox bookmarks are marked by a GUID which is an arbitrary 12-character
    base64 string.
    """
    rand_bytes = bytes(random.getrandbits(8) for _ in range(9))
    # -_ instead of +/ for the symbol characters
    return b64encode(rand_bytes, b'-_').decode()

def all_bookmarks(bookmark: dict) -> Iterable[dict]:
    # I think this is a fucking monad
    yield bookmark

    for child in bookmark.get('children', []):
        for grandchild in all_bookmarks(child):
            yield grandchild

def next_index(bookmark: dict) -> int:
    return 1 + max(map(lambda b: b['index'], bookmark.get('children', [])),
                   default=-1)

def next_id(root_bookmark: dict) -> int:
    return 1 + max(map(lambda b: b['id'], all_bookmarks(root_bookmark)),
                   default=-1)

def insert_bookmarks(root_bookmark: dict,
                     folder_title: str,
                     bookmarks: Iterable[dict]) -> dict:
    folder = next(filter(lambda b: b['title'] == folder_title,
                         all_bookmarks(root_bookmark)))
    folder.setdefault('children', [])
    start_id = next_id(root_bookmark)
    start_index = next_index(folder)
    for i, bookmark in enumerate(bookmarks):
        bookmark['id'] = start_id + i
        bookmark['index'] = start_index + i
        folder['children'].append(bookmark)
    return root_bookmark

@dataclass
class SearchEngine:
    """Why this order?
    $ sqlite3
    sqlite> .open "/mnt/c/Users/arvensis/AppData/Local/Google/Chrome/User Data/Default/Web Data"
    sqlite> PRAGMA TABLE_INFO(keywords);
    """
    id: int
    short_name: str
    keyword: str
    favicon_url: str
    url: str
    safe_for_autoreplace: int
    originating_url: str
    date_created: int
    usage_count: int
    input_encodings: str
    suggest_url: str
    prepopulate_id: int
    created_by_policy: int
    last_modified: int
    sync_guid: str
    alternate_urls: str
    image_url: str
    search_url_post_params: str
    suggest_url_post_params: str
    image_url_post_params: str
    new_tab_url: str
    last_visited: int

    def to_firefox(self, id: int = 0, index: int = 0):
        return {
            'dateAdded': self.date_created,
            'lastModified': self.last_modified,
            'guid': firefox_guid(),
            'id': id,  # Globally unique
            'type': 'text/x-moz-place',
            'index': index,  # Unique per-folder
            'typeCode': 1,  # 1 = bookmark, 2 = folder
            'uri': self.url.replace('{searchTerms}', '%s'),
            'title': self.short_name,
            'keyword': self.keyword,
            'postData': None,  # No equivalent in chrome
        }

def search_engines(db: os.PathLike):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query = 'select * from {}'.format(SEARCH_ENGINES_TABLE)
    engines = [
        SearchEngine(*engine)
        for engine
        in c.execute(query).fetchall()
    ]
    conn.close()
    return engines

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType(encoding='utf-8'))
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), default=sys.stdout)
    parser.add_argument('-t', '--title', default='Search Engines')
    parser.add_argument('-d', '--database', default=DATABASE_FNAME)
    args = parser.parse_args()

    bookmark = json.load(args.infile)
    engines = search_engines(args.database)
    insert_bookmarks(bookmark,
                     args.title,
                     map(SearchEngine.to_firefox, engines))
    json.dump(bookmark, args.outfile, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
