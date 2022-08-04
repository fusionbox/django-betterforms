try:
    from django.urls import re_path
except ImportError:
    # BBB: Django <2.0
    from django.conf.urls import url as re_path

from formtools.wizard.views import SessionWizardView

from .forms import Step1Form, Step2Form


class TestWizardView(SessionWizardView):
    def done(self, form_list, **kwargs):
        context = {
            'form_list': form_list,
        }
        return self.render_to_response(context)


urlpatterns = [
    re_path(r'^test-wizard-view/$', TestWizardView.as_view([Step1Form, Step2Form]), name='test_wizard'),
]
