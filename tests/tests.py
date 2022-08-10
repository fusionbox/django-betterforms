from collections import OrderedDict

from django.test import TestCase
from django.test.client import RequestFactory
from django.views.generic import CreateView
try:
    from django.utils.encoding import force_str
except ImportError:
    # BBB: Django <= 2.2
    from django.utils.encoding import force_text as force_str
from django.urls import reverse

from .models import User, Profile, Badge, Book
from .forms import (
    UserProfileMultiForm, BadgeMultiForm, ErrorMultiForm, MixedForm,
    NeedsFileField, ManyToManyMultiForm, RaisesErrorBookMultiForm,
    CleanedBookMultiForm, BookMultiForm, RaisesErrorCustomCleanMultiform,
    ModifiesDataCustomCleanMultiform,
)


class MultiFormTest(TestCase):
    def test_initial_data(self):
        form = UserProfileMultiForm(
            initial={
                'user': {
                    'name': 'foo',
                },
                'profile': {
                    'display_name': 'bar',
                }
            }
        )

        self.assertEqual(form['user']['name'].value(), 'foo')
        self.assertEqual(form['profile']['display_name'].value(), 'bar')

    def test_iter(self):
        form = UserProfileMultiForm()
        # get the field off of the BoundField
        fields = [field.field for field in form]
        self.assertEqual(fields, [
            form['user'].fields['name'],
            form['profile'].fields['name'],
            form['profile'].fields['display_name'],
        ])

    def test_as_table(self):
        form = UserProfileMultiForm()
        user_table = form['user'].as_table()
        profile_table = form['profile'].as_table()
        self.assertEqual(form.as_table(), user_table + profile_table)

    def test_fields(self):
        form = UserProfileMultiForm()
        self.assertEqual(form.fields, [
            'user-name', 'profile-name', 'profile-display_name'
        ])

    def test_errors(self):
        form = ErrorMultiForm()
        self.assertEqual(form.errors, {})

    def test_errors_crossform(self):
        form = ErrorMultiForm()
        form.add_crossform_error("Error")
        self.assertEqual(form.errors, {'__all__': ['Error']})

    def test_to_str_is_as_table(self):
        form = UserProfileMultiForm()
        self.assertEqual(force_str(form), form.as_table())

    def test_as_ul(self):
        form = UserProfileMultiForm()
        user_ul = form['user'].as_ul()
        profile_ul = form['profile'].as_ul()
        self.assertEqual(form.as_ul(), user_ul + profile_ul)

    def test_as_p(self):
        form = UserProfileMultiForm()
        user_p = form['user'].as_p()
        profile_p = form['profile'].as_p()
        self.assertEqual(form.as_p(), user_p + profile_p)

    def test_is_not_valid(self):
        form = UserProfileMultiForm({
            'user-name': 'foo',
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(form['user'].is_valid())
        self.assertFalse(form['profile'].is_valid())

        form = UserProfileMultiForm({
            'user-name': 'foo',
            'profile-name': 'foo',
        })
        self.assertTrue(form.is_valid())

    def test_non_field_errors(self):
        # we have to pass in a value for data to force real
        # validation.
        form = ErrorMultiForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors().as_text(),
                         '* It broke\n* It broke')

    def test_is_multipart(self):
        form1 = ErrorMultiForm()
        self.assertFalse(form1.is_multipart())

        form2 = NeedsFileField()
        self.assertTrue(form2.is_multipart())

    def test_media(self):
        form = NeedsFileField()
        self.assertIn('test.js', form.media._js)

    def test_is_bound(self):
        form = ErrorMultiForm()
        self.assertFalse(form.is_bound)
        form = ErrorMultiForm(data={})
        self.assertTrue(form.is_bound)

    def test_hidden_fields(self):
        form = NeedsFileField()

        hidden_fields = [field.field for field in form.hidden_fields()]

        self.assertEqual(hidden_fields, [
            form['file'].fields['hidden'],
            form['errors'].fields['hidden'],
        ])

    def test_visible_fields(self):
        form = NeedsFileField()

        visible_fields = [field.field for field in form.visible_fields()]

        self.assertEqual(visible_fields, [
            form['file'].fields['date'],
            form['file'].fields['image'],
            form['errors'].fields['name'],
        ])

    def test_prefix(self):
        form = ErrorMultiForm(prefix='foo')
        self.assertEqual(form['errors'].prefix, 'errors__foo')

    def test_cleaned_data(self):
        form = UserProfileMultiForm({
            'user-name': 'foo',
            'profile-name': 'foo',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, OrderedDict([
            ('user', {
                'name': 'foo',
            }),
            ('profile', {
                'name': 'foo',
                'display_name': '',
            }),
        ]))

    def test_handles_none_initial_value(self):
        # Used to throw an AttributeError
        UserProfileMultiForm(initial=None)

    def test_works_with_wizard_view(self):
        url = reverse('test_wizard')
        self.client.get(url)

        response = self.client.post(url, {
            'test_wizard_view-current_step': '0',
            'profile__0-name': 'John Doe',
        })
        view = response.context['view']
        self.assertEqual(view.storage.current_step, '1')

        response = self.client.post(url, {
            'test_wizard_view-current_step': '1',
            '1-confirm': True,
        })
        form_list = response.context['form_list']
        # In Django>=1.7 on Python 3, form_list is a ValuesView, which doesn't
        # support indexing, you are probably recommending to use form_dict
        # instead of form_list on Django>=1.7 anyway though.
        form_list = list(form_list)
        self.assertEqual(form_list[0]['profile'].cleaned_data['name'],
                         'John Doe')

    def test_custom_clean_errors(self):
        form = RaisesErrorCustomCleanMultiform({
            'user-name': 'foo',
            'profile-name': 'foo',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.cleaned_data, OrderedDict([
            ('user', {
                'name': u'foo'
            }),
            ('profile', {
                'name': u'foo',
                'display_name': u'',
            })
        ]))
        self.assertEqual(form.non_field_errors().as_text(), '* It broke')

    def test_custom_clean_data_change(self):
        form = ModifiesDataCustomCleanMultiform({
            'user-name': 'foo',
            'profile-name': 'foo',
            'profile-display_name': 'uncleaned name',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, OrderedDict([
            ('user', {
                'name': u'foo'
            }),
            ('profile', {
                'name': u'foo',
                'display_name': u'cleaned name',
            })
        ]))


class MultiModelFormTest(TestCase):
    def test_save(self):
        form = BadgeMultiForm({
            'badge1-name': 'foo',
            'badge1-color': 'blue',
            'badge2-name': 'bar',
            'badge2-color': 'purple',
        })

        objects = form.save()
        self.assertEqual(objects['badge1'], Badge.objects.get(name='foo'))
        self.assertEqual(objects['badge2'], Badge.objects.get(name='bar'))

    def test_save_m2m(self):
        book1 = Book.objects.create(name='Foo')
        Book.objects.create(name='Bar')

        form = ManyToManyMultiForm({
            'badge-name': 'badge name',
            'badge-color': 'badge color',
            'author-name': 'author name',
            'author-books': [
                book1.pk,
            ],
        })

        self.assertTrue(form.is_valid())

        objects = form.save(commit=False)
        objects['badge'].save()
        objects['author'].save()
        self.assertEqual(objects['author'].books.count(), 0)

        form.save_m2m()
        self.assertEqual(objects['author'].books.get(), book1)

    def test_instance(self):
        user = User(name='foo')
        profile = Profile(display_name='bar')

        # Django checks model equality by checking that the pks are the same.
        # A User with no pk is the same as any other User with no pk.
        user.pk = 1
        profile.pk = 1

        form = UserProfileMultiForm(
            instance={
                'user': user,
                'profile': profile,
            }
        )

        self.assertEqual(form['user'].instance, user)
        self.assertEqual(form['profile'].instance, profile)

    def test_model_and_non_model_forms(self):
        # This tests that it is possible to instantiate a non-model form using
        # the MultiModelForm class too, previously it would explode because it
        # was being passed an instance parameter.
        MixedForm()

    def test_works_with_create_view_get(self):
        viewfn = CreateView.as_view(
            form_class=UserProfileMultiForm,
            template_name='noop.html',
        )
        factory = RequestFactory()
        request = factory.get('/')
        # This would fail as CreateView passes instance=None
        viewfn(request)

    def test_works_with_create_view_post(self):
        viewfn = CreateView.as_view(
            form_class=BadgeMultiForm,
            # required after success
            success_url='/',
            template_name='noop.html',
        )
        factory = RequestFactory()
        request = factory.post('/', data={
            'badge1-name': 'foo',
            'badge1-color': 'blue',
            'badge2-name': 'bar',
            'badge2-color': 'purple',
        })
        resp = viewfn(request)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Badge.objects.count(), 2)

    def test_is_valid_with_formset(self):
        form = BookMultiForm({
            'book-name': 'Test',
            'images-0-name': 'One',
            'images-1-name': 'Two',
            'images-TOTAL_FORMS': '3',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
        })
        assert form.is_valid()

    def test_override_clean(self):
        form = CleanedBookMultiForm({
            'book-name': 'Test',
            'images-0-name': 'One',
            'images-1-name': 'Two',
            'images-TOTAL_FORMS': '3',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
        })
        assert form.is_valid()
        assert form['book'].cleaned_data['name'] == 'Overridden'
        assert form['images'].forms[0].cleaned_data['name'] == 'Two'
        assert form['images'].forms[1].cleaned_data['name'] == 'Three'

    def test_non_field_errors_with_formset(self):
        form = RaisesErrorBookMultiForm({
            'book-name': '',
            'images-0-name': '',
            'images-TOTAL_FORMS': '3',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
        })
        # assertDoesntRaise AttributeError
        self.assertEqual(form.non_field_errors().as_text(), '* It broke')
