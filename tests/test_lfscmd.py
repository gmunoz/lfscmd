import unittest

class TestLfscmd(unittest.TestCase):
    def test_chapters(self):
        from lfscmd import chapter_paths
        chapters = chapter_paths('lfs.git')
        self.assertEqual(len(chapters), 11)

    def test_entitiy_paths(self):
        from lfscmd import ent_paths
        entity_paths = ent_paths('lfs.git')
        self.assertEqual(len(entity_paths), 3)
