"""Regression tests for optional new Stellen text blocks."""
import json
from unittest.mock import Mock
from django.test import SimpleTestCase
from recruiting.views import _save_vacancy_new_blocks


class VacancyBlockSavingTests(SimpleTestCase):
    def setUp(self):
        self.model = Mock()
        self.model.objects.get_or_create.return_value = (Mock(), True)

    def test_valid_block_is_created_inactive(self):
        _save_vacancy_new_blocks(json.dumps([
            {"category": "benefits", "text": "  Flexible Arbeitszeiten  ", "profession": "IT"}
        ]), self.model)
        self.model.objects.get_or_create.assert_called_once_with(
            category="benefits", text="Flexible Arbeitszeiten",
            defaults={"profession": "IT", "active": False},
        )

    def test_invalid_json_does_not_write(self):
        _save_vacancy_new_blocks("{invalid", self.model)
        self.model.objects.get_or_create.assert_not_called()

    def test_non_list_does_not_write(self):
        _save_vacancy_new_blocks('{"category":"benefits"}', self.model)
        self.model.objects.get_or_create.assert_not_called()

    def test_unsupported_category_and_blank_text_are_skipped(self):
        _save_vacancy_new_blocks(json.dumps([
            {"category": "published", "text": "Never"},
            {"category": "benefits", "text": "  "},
            None,
        ]), self.model)
        self.model.objects.get_or_create.assert_not_called()

    def test_limit_of_100_items_is_preserved(self):
        _save_vacancy_new_blocks(json.dumps([
            {"category": "benefits", "text": str(i)} for i in range(110)
        ]), self.model)
        self.assertEqual(self.model.objects.get_or_create.call_count, 100)

    def test_text_and_profession_lengths_are_limited(self):
        _save_vacancy_new_blocks(json.dumps([
            {"category": "responsibilities", "text": "x"*400, "profession": "p"*60}
        ]), self.model)
        kwargs = self.model.objects.get_or_create.call_args.kwargs
        self.assertEqual(len(kwargs["text"]), 300)
        self.assertEqual(len(kwargs["defaults"]["profession"]), 40)
