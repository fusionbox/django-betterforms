from django.urls import path

from formtools.wizard.views import SessionWizardView

from .forms import Step1Form, Step2Form


class TestWizardView(SessionWizardView):
    def done(self, form_list, **kwargs):
        context = {
            'form_list': form_list,
        }
        return self.render_to_response(context)


urlpatterns = [
    path('test-wizard-view/', TestWizardView.as_view([Step1Form, Step2Form]), name='test_wizard'),
]
