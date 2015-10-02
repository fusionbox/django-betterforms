import django
from django.conf.urls import url

if django.VERSION >= (1, 8):
    from formtools.wizard.views import SessionWizardView
else:
    from django.contrib.formtools.wizard.views import SessionWizardView

from .forms import Step1Form, Step2Form


class TestWizardView(SessionWizardView):
    def get_context_data(self, **kwargs):
        kwargs = super(TestWizardView, self).get_context_data(**kwargs)
        # Django < 1.5 does not set the view object in the context
        kwargs['view'] = self
        return kwargs

    def done(self, form_list, **kwargs):
        context = {
            'form_list': form_list,
        }
        return self.render_to_response(context)


urlpatterns = [
    url(r'^test-wizard-view/$', TestWizardView.as_view([Step1Form, Step2Form]), name='test_wizard'),
]
