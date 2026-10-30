import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from library_index import build_index, search


class LibraryIndexTests(unittest.TestCase):
  def test_index_captures_book_author_and_chapter(self):
    with tempfile.TemporaryDirectory() as temp:
      root = Path(temp) / 'library'
      book = root / '文学作品' / '远方的书'
      book.mkdir(parents=True)
      (root / '文学作品' / 'summaries.json').write_text('{"远方的书":"一部测试作品"}', encoding='utf-8')
      (book / '第一章.mp3').write_bytes(b'audio')
      with zipfile.ZipFile(book / 'book.epub', 'w') as archive:
        archive.writestr('META-INF/container.xml', '<container><rootfiles><rootfile full-path="OPS/content.opf"/></rootfiles></container>')
        archive.writestr('OPS/content.opf', '<package><metadata><dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">测试作者</dc:creator></metadata></package>')
      db_path = Path(temp) / 'sync.sqlite3'
      self.assertEqual(build_index(db_path, root, '/多媒体/750HD/有声书'), {'books': 1, 'chapters': 1})
      with sqlite3.connect(db_path) as db:
        by_author = search(db, '测试作者')
        by_chapter = search(db, '第一章')
      self.assertEqual(by_author[0]['title'], '远方的书')
      self.assertTrue(any(row['kind'] == 'chapter' for row in by_chapter))


if __name__ == '__main__':
  unittest.main()
