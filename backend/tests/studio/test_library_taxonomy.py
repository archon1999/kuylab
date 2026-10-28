from django.test import SimpleTestCase
from apps.studio.library_taxonomy import COLLECTIONS, GROUPS, WORK_COLLECTION, taxonomy
from apps.studio.repertoire import SOURCES
from apps.studio.content import localize


class LibraryTaxonomyTests(SimpleTestCase):
    def test_every_current_work_has_one_browsing_collection(self):
        codes = [code for _, _, codes in COLLECTIONS.values() for code in codes]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(set(codes), {source.code for source in SOURCES})
        self.assertEqual(set(WORK_COLLECTION), set(codes))
        self.assertTrue(all(group in GROUPS for group, _, _ in COLLECTIONS.values()))

    def test_classical_editions_share_composer_collection(self):
        for code in ('ode-to-joy', 'moonlight-sonata', 'beethoven-moonlight-sonata-movement-3', 'fur-elise'):
            self.assertEqual(taxonomy(code)['library_group']['id'], 'classical')
            self.assertEqual(taxonomy(code)['library_collection']['id'], 'beethoven')
        self.assertEqual(taxonomy('prelude-e-minor')['library_collection']['id'], 'chopin')
        self.assertEqual(taxonomy('waltz-a-minor')['library_collection']['id'], 'chopin')

    def test_franchises_share_collections_and_labels_are_localized(self):
        self.assertEqual(taxonomy('naruto-senya')['library_collection']['id'], taxonomy('boruto-spin-and-burst-reverse-situation')['library_collection']['id'])
        for language in ('uz', 'ru', 'en'):
            for source in SOURCES:
                value = localize(taxonomy(source.code), language)
                self.assertIsInstance(value['library_group']['label'], str)
                self.assertIsInstance(value['library_collection']['label'], str)
