#!/usr/bin/env python3
"""Synthetic-only regression tests of sensitive intake and source conflicts."""
import unittest
from stage3b_source_integrity import classify_source, review_manifest, numeric_conflicts


class SourceIntegrityTest(unittest.TestCase):
    def test_signed_stakeholder_is_restricted(self):
        self.assertEqual(classify_source('Signed Stakeholder Engagement ALPHA.docx'),
                         'signed_derivative_restricted')

    def test_signed_communique_is_restricted(self):
        self.assertEqual(classify_source('Signed communiqué SAMPLE.pdf'),
                         'signed_derivative_restricted')

    def test_signature_folder_is_restricted(self):
        self.assertEqual(classify_source('document.pdf', 'Event/Signatures'),
                         'signatures_restricted')

    def test_attendance_images_are_restricted(self):
        self.assertEqual(classify_source('IMG_1011.JPG', 'Meeting/Attendance'),
                         'attendance_restricted')

    def test_exclude_temporary_file(self):
        self.assertEqual(classify_source('~WRL0123.tmp'), 'temporary_exclude')

    def test_unsigned_communique_remains_candidate(self):
        self.assertEqual(classify_source('communiqué SAMPLE.docx'), 'communique_candidate')

    def test_sensitive_misclassification_detected_without_names(self):
        report = review_manifest([
            {'filename':'Signed Stakeholder Engagement ALPHA.docx',
             'initial_category':'thematic_or_supporting_input'},
            {'filename':'communiqué ALPHA.docx',
             'initial_category':'communique_candidate'}])
        self.assertEqual(report['misclassified_source_entries'], 1)
        self.assertEqual(report['restricted_sources'], 1)
        self.assertEqual(report['authorized_public_records'], 0)
        self.assertNotIn('ALPHA', str(report))

    def test_conflicting_quantities_preserved_not_selected(self):
        rows = [
            {'reviewed_asset_key':'SYN-ONE', 'source_locator':'sheet 1 row 2',
             'quantity':1.5, 'unit':'MCM'},
            {'reviewed_asset_key':'SYN-ONE', 'source_locator':'sheet 2 row 4',
             'quantity':2.5, 'unit':'MCM'},
        ]
        report = numeric_conflicts(rows)
        self.assertEqual(report['flag_counts']['QUANTITY_CONFLICT_REVIEW'],1)
        self.assertEqual(report['quantities_verified'],0)

    def test_different_asset_keys_do_not_join_on_name(self):
        rows = [
            {'reviewed_asset_key':'SYN-ONE-A', 'source_locator':'row 1',
             'quantity':1.0,'unit':'MCM'},
            {'reviewed_asset_key':'SYN-ONE-B', 'source_locator':'row 2',
             'quantity':3.0,'unit':'MCM'},
        ]
        self.assertEqual(numeric_conflicts(rows)['explicitly_comparable_groups'],0)

    def test_no_implicit_unit_conversion(self):
        rows = [
            {'reviewed_asset_key':'SYN-X','source_locator':'a',
             'quantity':3,'unit':'m3'},
            {'reviewed_asset_key':'SYN-X','source_locator':'b',
             'quantity':3,'unit':'MCM'},
        ]
        result=numeric_conflicts(rows)
        self.assertEqual(result['flag_counts']['UNIT_CONFLICT_REVIEW'],1)
        self.assertNotIn('QUANTITY_CONFLICT_REVIEW',result['flag_counts'])

    def test_missing_quantity_not_zero(self):
        rows = [
            {'reviewed_asset_key':'SYN-X','source_locator':'a',
             'quantity':None,'unit':'MCM'},
            {'reviewed_asset_key':'SYN-X','source_locator':'b',
             'quantity':1,'unit':'MCM'},
        ]
        result=numeric_conflicts(rows)
        self.assertEqual(result['flag_counts']['MISSING_VALUE_OR_UNIT'],1)
        self.assertNotIn('QUANTITY_CONFLICT_REVIEW',result['flag_counts'])

    def test_reject_boolean_numeric(self):
        with self.assertRaises(ValueError):
            numeric_conflicts([{'reviewed_asset_key':'SYN','source_locator':'a',
                                'quantity':True,'unit':'MCM'}])


if __name__ == '__main__':
    unittest.main()
