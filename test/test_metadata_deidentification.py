# -*- coding: utf-8 -*-

import os
import tempfile

import unittest
from random import choice, randint
import string

import pandas as pd

from kskit.dicom.deid_mammogram import (
    load_recipe,
    get_general_rule,
    offset4date,
    gen_dicom_uid,
    deidentify_attributes,
)

from kskit.test_deid_mammogram import (
    levenshtein_distance
)

ORG_ROOT: str = "9.9.9.9.9"


class MetadataDeidentificationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """this method is called before once before running all tests"""
        super(MetadataDeidentificationTest, cls).setUpClass()
        cls.recipe = load_recipe()
        cls.test_assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        cls.test_mammo_dir = os.path.join(
            cls.test_assets_dir, 'sample_mammograms')

    def test_regex(self):
        """test function for get_general_rule()"""
        self.assertEqual(get_general_rule(
            '0x50ffffff', self.recipe), 'RETIRER')
        self.assertEqual(get_general_rule(
            '0x50a23e56', self.recipe), 'RETIRER')
        self.assertEqual(get_general_rule(
            '0x50123456', self.recipe), 'RETIRER')
        self.assertEqual(get_general_rule(
            '0x60003000', self.recipe), 'RETIRER')
        self.assertEqual(get_general_rule(
            '0x60004000', self.recipe), 'RETIRER')
        self.assertEqual(get_general_rule(
            '0x60564000', self.recipe), 'RETIRER')
        self.assertEqual(get_general_rule(
            '0x605d3000', self.recipe), 'RETIRER')

    def test_offset4date(self):
        """test function for offset4date"""
        self.assertEqual(offset4date('19930822', 1), '19930821')
        self.assertEqual(offset4date('20211119', 56), '20210924')
        self.assertEqual(offset4date('18700107', 890), '18670801')
        self.assertEqual(offset4date('20250101', -78), '20250320')
        self.assertEqual(offset4date('20010422', 678), '19990614')
        self.assertEqual(offset4date('22010122', 56), '22001127')
        self.assertEqual(offset4date('56090102', 15), '56081218')
        self.assertEqual(offset4date('20090608', 187), '20081203')

    def test_gen_uuid(self):
        """test function for gen_dicom_uid"""
        already_seen = []
        for _ in range(0, 9999):
            patient_id = ''.join(choice(string.ascii_letters)
                                 for _ in range(randint(5, 30)))
            guid = ''.join(choice(string.digits) for _ in range(30))
            new_hash = gen_dicom_uid(patient_id, guid, org_root="1.2.3.4")
            # Tests for duplicates on 10k hashes generated
            self.assertTrue(new_hash not in already_seen)
            already_seen.append(new_hash)
            # Tests if the operation can be reproduced
            self.assertEqual(gen_dicom_uid(
                patient_id, guid, org_root="1.2.3.4"), new_hash)

    def test_levenshtein_distance(self):
        """test function for levenshtein_distance"""
        self.assertEqual(levenshtein_distance("chien", "niche"), 4)
        self.assertEqual(levenshtein_distance(
            "javawasneat", "scalaisgreat"), 7)
        self.assertEqual(levenshtein_distance("forward", "drawrof"), 6)
        self.assertEqual(levenshtein_distance("distance", "eistancd"), 2)
        self.assertEqual(levenshtein_distance("sturgeon", "urgently"), 6)
        self.assertEqual(levenshtein_distance("difference", "distance"), 5)
        self.assertEqual(levenshtein_distance("example", "samples"), 3)
        self.assertEqual(levenshtein_distance("bsfhebfkrn", "bsthebtkrn"), 2)
        self.assertEqual(levenshtein_distance("cie", "cle"), 1)

    def test_deidentify_attributes(self):
        """nominal case"""
        with tempfile.TemporaryDirectory() as outdirpath:
            df = deidentify_attributes(
                self.test_mammo_dir,
                outdirpath,
                org_root="9.9.9.9.9",
                erase_outdir=False
            )

            self.assertIsInstance(df, pd.DataFrame)
