try:
    from django.utils import unittest
except ImportError:
    import unittest  # NOQA

import django
from django import forms
from django.db import models
from django.test import TestCase
from django.template.loader import render_to_string

from betterforms.forms import (
    BetterForm, BetterModelForm, Fieldset, BoundFieldset, flatten_to_tuple,
)


class TestUtils(TestCase):
    def test_flatten(self):
        fields1 = ('a', 'b', 'c')
        self.assertTupleEqual(flatten_to_tuple(fields1), fields1)

        fields2 = ('a', ('b', 'c'), 'd')
        self.assertTupleEqual(flatten_to_tuple(fields2), ('a', 'b', 'c', 'd'))

        fields3 = ('a', ('b', 'c'), 'd', ('e', ('f', 'g', ('h',)), 'i'))
        self.assertTupleEqual(flatten_to_tuple(fields3), ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'))


class TestFieldSets(TestCase):
    def test_basic_fieldset(self):
        fields = ('a', 'b', 'c')
        fieldset = Fieldset('the_name', fields=fields)
        self.assertEqual(fieldset.name, 'the_name')
        self.assertTupleEqual(fields, fieldset.fields)

    def test_nested_fieldset(self):
        fields = ('a', ('b', 'c'), 'd')
        fieldset = Fieldset('the_name', fields=fields)
        self.assertTupleEqual(flatten_to_tuple(fields), fieldset.fields)
        iterated = tuple(iter(fieldset))
        self.assertEqual(iterated[0], 'a')
        self.assertTupleEqual(iterated[1].fields, ('b', 'c'))
        self.assertEqual(iterated[2], 'd')

    def test_named_nested_fieldset(self):
        fields = ('a', ('sub_name', {'fields': ('b', 'c')}), 'd')
        fieldset = Fieldset('the_name', fields=fields)
        self.assertTupleEqual(fieldset.fields, ('a', 'b', 'c', 'd'))
        fieldsets = tuple(iter(fieldset))
        self.assertEqual(fieldsets[0], 'a')
        self.assertTupleEqual(fieldsets[1].fields, ('b', 'c'))
        self.assertEqual(fieldsets[1].name, 'sub_name')
        self.assertEqual(fieldsets[2], 'd')

    def test_deeply_nested_fieldsets(self):
        fields = ('a', ('b', 'c'), 'd', ('e', ('f', 'g', ('h',)), 'i'))
        fieldset = Fieldset('the_name', fields=fields)
        self.assertTupleEqual(flatten_to_tuple(fields), fieldset.fields)

    def test_fieldset_as_row_item(self):
        fields = ('a', Fieldset('sub_name', fields=['b', 'c']))
        fieldset = Fieldset('the_name', fields=fields)
        self.assertTupleEqual(fieldset.fields, ('a', 'b', 'c'))

    def test_nonzero_fieldset(self):
        fieldset1 = Fieldset('the_name', fields=[])
        self.assertFalse(fieldset1)

        fieldset2 = Fieldset('the_name', fields=['a'])
        self.assertTrue(fieldset2)

    def test_assigning_template_name(self):
        fieldset1 = Fieldset('the_name', fields=['a'])
        self.assertIsNone(fieldset1.template_name)
        fieldset2 = Fieldset('the_name', fields=['a'], template_name='some_custom_template.html')
        self.assertEqual(fieldset2.template_name, 'some_custom_template.html')


class TestFieldsetDeclarationSyntax(TestCase):
    def test_admin_style_declaration(self):
        class TestForm(BetterForm):
            a = forms.CharField()
            b = forms.CharField()
            c = forms.CharField()
            d = forms.CharField()

            class Meta:
                fieldsets = (
                    ('first', {'fields': ('a')}),
                    ('second', {'fields': ('b', 'c')}),
                    ('third', {'fields': ('d')}),
                )
        form = TestForm()
        fieldsets = [fieldset for fieldset in form.fieldsets]
        self.assertEqual(fieldsets[0].name, 'first')
        self.assertTupleEqual(fieldsets[0].fieldset.fields, ('a',))
        self.assertEqual(fieldsets[1].name, 'second')
        self.assertTupleEqual(fieldsets[1].fieldset.fields, ('b', 'c'))
        self.assertEqual(fieldsets[2].name, 'third')
        self.assertTupleEqual(fieldsets[2].fieldset.fields, ('d',))
        self.assertIsInstance(fieldsets[0], BoundFieldset)

    def test_bare_fields_style_declaration(self):
        class TestForm(BetterForm):
            a = forms.CharField()
            b = forms.CharField()
            c = forms.CharField()
            d = forms.CharField()

            class Meta:
                fieldsets = ('a', ('b', 'c'), 'd')
        form = TestForm()
        fieldsets = [fieldset for fieldset in form.fieldsets]
        self.assertEqual(fieldsets[0].field, form.fields['a'])
        self.assertEqual(fieldsets[1].name, '__base_fieldset___1')
        self.assertTupleEqual(fieldsets[1].fieldset.fields, ('b', 'c'))
        self.assertEqual(fieldsets[2].field, form.fields['d'])
        self.assertIsInstance(fieldsets[0], forms.forms.BoundField)
        self.assertIsInstance(fieldsets[1], BoundFieldset)
        self.assertIsInstance(fieldsets[2], forms.forms.BoundField)


class TestBetterForm(TestCase):
    def setUp(self):
        class TestForm(BetterForm):
            a = forms.CharField()
            b = forms.CharField()
            c = forms.CharField()

            class Meta:
                fieldsets = (
                    ('first', {'fields': ('a', 'b')}),
                    ('second', {'fields': ('c')}),
                )
        self.TestForm = TestForm

    def test_name_lookups(self):
        form = self.TestForm()
        fieldsets = [fieldset for fieldset in form.fieldsets]
        # field lookups
        self.assertEqual(form['a'].field, fieldsets[0]['a'].field)
        # fieldset lookups
        self.assertEqual(form['first'].fieldset, fieldsets[0].fieldset)
        self.assertEqual(form['second'].fieldset, fieldsets[1].fieldset)

    def test_index_lookups(self):
        form = self.TestForm()
        # field lookups
        self.assertEqual(form['a'].field, form.fieldsets[0][0].field)
        # fieldset lookups
        self.assertEqual(form['first'].fieldset, form.fieldsets[0].fieldset)
        self.assertEqual(form['second'].fieldset, form.fieldsets[1].fieldset)

    def test_field_to_fieldset_name_conflict(self):
        with self.assertRaises(AttributeError):
            class NameConflictForm(self.TestForm):
                class Meta:
                    fieldsets = (
                        ('first', {'fields': ('a', 'b')}),
                        ('first', {'fields': ('c')}),
                    )

    def test_duplicate_name_in_fieldset(self):
        with self.assertRaises(AttributeError):
            class NameConflictForm(self.TestForm):
                class Meta:
                    fieldsets = (
                        ('first', {'fields': ('a', 'a')}),
                        ('second', {'fields': ('c')}),
                    )

    def test_field_error(self):
        data = {'a': 'a', 'b': 'b', 'c': 'c'}
        form = self.TestForm(data)
        self.assertTrue(form.is_valid())

        form.field_error('a', 'test')
        self.assertFalse(form.is_valid())

    def test_form_error(self):
        data = {'a': 'a', 'b': 'b', 'c': 'c'}
        form = self.TestForm(data)
        self.assertTrue(form.is_valid())

        form.form_error('test')
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'__all__': [u'test']})

    def test_fieldset_error(self):
        data = {'a': 'a', 'b': 'b', 'c': 'c'}
        form = self.TestForm(data)
        self.assertTrue(form.is_valid())

        self.assertNotIn(form.fieldsets[0].fieldset.error_css_class, form.fieldsets[0].css_classes)

        form.field_error('first', 'test')
        self.assertFalse(form.is_valid())
        fieldsets = [fieldset for fieldset in form.fieldsets]
        self.assertTrue(fieldsets[0].errors)
        self.assertIn(form.fieldsets[0].fieldset.error_css_class, form.fieldsets[0].css_classes)

    def test_fieldset_css_classes(self):
        class TestForm(BetterForm):
            a = forms.CharField()
            b = forms.CharField()
            c = forms.CharField()

            class Meta:
                fieldsets = (
                    ('first', {'fields': ('a', 'b')}),
                    ('second', {'fields': ('c'), 'css_classes': ['arst', 'tsra']}),
                )
        form = TestForm()
        self.assertIn('arst', form.fieldsets[1].css_classes)
        self.assertIn('tsra', form.fieldsets[1].css_classes)

    def test_fieldset_iteration(self):
        form = self.TestForm()
        self.assertTupleEqual(
            tuple(fieldset.fieldset for fieldset in form),
            tuple(fieldset.fieldset for fieldset in form.fieldsets),
        )

    def test_no_fieldsets(self):
        class TestForm(BetterForm):
            a = forms.CharField()
            b = forms.CharField()
            c = forms.CharField()

        form = TestForm()
        fields = [field.field for field in form]
        self.assertItemsEqual(fields, form.fields.values())


class TestBetterModelForm(TestCase):
    def setUp(self):
        class TestModel(models.Model):
            a = models.CharField(max_length=255)
            b = models.CharField(max_length=255)
            c = models.CharField(max_length=255)
            d = models.CharField(max_length=255)
        self.TestModel = TestModel

    def test_basic_fieldsets(self):
        class TestModelForm(BetterModelForm):
            class Meta:
                model = self.TestModel
                fieldsets = (
                    ('first', {'fields': ('a',)}),
                    ('second', {'fields': ('b', 'c')}),
                    ('third', {'fields': ('d',)}),
                )
        form = TestModelForm()
        fieldsets = [fieldset for fieldset in form.fieldsets]
        self.assertEqual(fieldsets[0].name, 'first')
        self.assertEqual(fieldsets[1].name, 'second')
        self.assertEqual(fieldsets[2].name, 'third')
        self.assertTupleEqual(fieldsets[0].fieldset.fields, ('a',))
        self.assertTupleEqual(fieldsets[1].fieldset.fields, ('b', 'c'))
        self.assertTupleEqual(fieldsets[2].fieldset.fields, ('d',))

    def test_fields_meta_attribute(self):
        class TestModelForm1(BetterModelForm):
            class Meta:
                model = self.TestModel
                fieldsets = (
                    ('first', {'fields': ('a',)}),
                    ('second', {'fields': ('b', 'c')}),
                    ('third', {'fields': ('d',)}),
                )
        self.assertTrue(hasattr(TestModelForm1.Meta, 'fields'))
        self.assertTupleEqual(TestModelForm1.Meta.fields, ('a', 'b', 'c', 'd'))

        class TestModelForm2(BetterModelForm):
            class Meta:
                model = self.TestModel
                fieldsets = (
                    ('first', {'fields': ('a',)}),
                    ('second', {'fields': ('b', 'c')}),
                    ('third', {'fields': ('d',)}),
                )
                fields = ('a', 'b', 'd')

        self.assertTrue(hasattr(TestModelForm2.Meta, 'fields'))
        self.assertTupleEqual(TestModelForm2.Meta.fields, ('a', 'b', 'd'))

        class TestModelForm3(TestModelForm2):
            pass

        self.assertTrue(hasattr(TestModelForm3.Meta, 'fields'))
        self.assertTupleEqual(TestModelForm3.Meta.fields, ('a', 'b', 'd'))

        class TestModelForm4(TestModelForm2):
            class Meta(TestModelForm2.Meta):
                fieldsets = (
                    ('first', {'fields': ('a', 'c')}),
                    ('third', {'fields': ('d',)}),
                )

        self.assertTrue(hasattr(TestModelForm4.Meta, 'fields'))
        self.assertTupleEqual(TestModelForm4.Meta.fields, ('a', 'c', 'd'))


class TestFormRendering(TestCase):
    def setUp(self):
        class TestForm(BetterForm):
            a = forms.CharField()
            b = forms.CharField()
            c = forms.CharField()

            class Meta:
                fieldsets = (
                    ('first', {'fields': ('a', 'b')}),
                    ('second', {'fields': ('c')}),
                )
        self.TestForm = TestForm

    @unittest.skipIf(django.get_version().startswith('1.3'), "Django < 1.4 doesn't have `assertHTMLEqual`")
    def test_include_tag_rendering(self):
        form = self.TestForm()
        env = {
            'form': form,
            'no_head': True,
            'fieldset_template_name': 'partials/fieldset_as_div.html',
            'field_template_name': 'partials/field_as_div.html',
        }
        self.assertHTMLEqual(
            render_to_string('partials/form_as_fieldsets.html', env),
            """
            <fieldset class="formFieldset first">
                <div class="required a formField">
                    <label for="id_a">A</label>
                    <input id="id_a" name="a" type="text" />
                </div>
                <div class="required b formField">
                    <label for="id_b">B</label>
                    <input id="id_b" name="b" type="text" />
                </div>
            </fieldset>
            <fieldset class="formFieldset second">
                <div class="required c formField">
                    <label for="id_c">C</label>
                    <input id="id_c" name="c" type="text" />
                </div>
            </fieldset>
            """,
        )
        form.field_error('a', 'this is an error message')
        self.assertHTMLEqual(
            render_to_string('partials/form_as_fieldsets.html', env),
            """
            <fieldset class="formFieldset first">
                <div class="required error a formField">
                    <label for="id_a">A</label>
                    <input id="id_a" name="a" type="text" />
                    <ul class="errorlist"><li>this is an error message</li></ul>
                </div>
                <div class="required b formField">
                    <label for="id_b">B</label>
                    <input id="id_b" name="b" type="text" />
                </div>
            </fieldset>
            <fieldset class="formFieldset second">
                <div class="required c formField">
                    <label for="id_c">C</label>
                    <input id="id_c" name="c" type="text" />
                </div>
            </fieldset>
            """,
        )

    @unittest.expectedFailure
    def test_form_to_str(self):
        # TODO: how do we test this
        assert False

    @unittest.expectedFailure
    def test_form_as_table(self):
        form = self.TestForm()
        form.as_table()

    @unittest.expectedFailure
    def test_form_as_ul(self):
        form = self.TestForm()
        form.as_ul()

    @unittest.skipIf(django.get_version().startswith('1.3'), "Django < 1.4 doesn't have `assertHTMLEqual`")
    def test_form_as_p(self):
        form = self.TestForm()
        self.assertHTMLEqual(
            form.as_p(),
            """
            <fieldset class="formFieldset first">
                <p class="required">
                    <label for="id_a">A</label>
                    <input id="id_a" name="a" type="text" />
                </p>
                <p class="required">
                    <label for="id_b">B</label>
                    <input id="id_b" name="b" type="text" />
                </p>
            </fieldset>
            <fieldset class="formFieldset second">
                <p class="required">
                    <label for="id_c">C</label>
                    <input id="id_c" name="c" type="text" />
                </p>
            </fieldset>
            """,
        )

        form.field_error('a', 'this is an error')
        self.assertHTMLEqual(
            form.as_p(),
            """
            <fieldset class="formFieldset first">
                <p class="required error">
                    <ul class="errorlist"><li>this is an error</li></ul>
                    <label for="id_a">A</label>
                    <input id="id_a" name="a" type="text" />
                </p>
                <p class="required">
                    <label for="id_b">B</label>
                    <input id="id_b" name="b" type="text" />
                </p>
            </fieldset>
            <fieldset class="formFieldset second">
                <p class="required">
                    <label for="id_c">C</label>
                    <input id="id_c" name="c" type="text" />
                </p>
            </fieldset>
            """,
        )
