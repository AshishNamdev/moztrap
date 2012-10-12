"""
Management forms for runs.

"""
import floppyforms as forms

from moztrap import model
from moztrap.view.lists import filters
from moztrap.view.utils import mtforms




class RunForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
    """Base form for adding/editing runs."""
    suites = mtforms.MTMultipleChoiceField(
        required=False,
        choice_attrs=mtforms.product_id_attrs,
        widget=mtforms.FilteredSelectMultiple(
            choice_template="manage/run/suite_select/_suite_select_item.html",
            listordering_template=(
                "manage/run/suite_select/_suite_select_listordering.html"),
            filters=[
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
        )
    productversion = mtforms.MTModelChoiceField(
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=mtforms.product_id_attrs)


    class Meta:
        model = model.Run
        fields = ["productversion", "name", "description", "start", "end"]
        widgets = {
            "name": forms.TextInput,
            "description": mtforms.BareTextarea,
            "start": forms.DateInput,
            "end": forms.DateInput,
            }


    def save(self, user=None):
        """Save and return run, with suite associations."""
        user = user or self.user
        run = super(RunForm, self).save(user=user)

        run.runsuites.all().delete(permanent=True)
        for i, suite_id in enumerate(self.cleaned_data["suites"]):
            suite = model.Suite.objects.get(pk=suite_id)
            model.RunSuite.objects.create(
                run=run, suite=suite, order=i, user=user)

        return run



class AddRunForm(RunForm):
    """Form for adding a run."""
    pass



class EditRunForm(RunForm):
    """Form for editing a run."""
    def __init__(self, *args, **kwargs):
        """Initialize EditRunForm; no changing product version of active run."""
        super(EditRunForm, self).__init__(*args, **kwargs)

        pvf = self.fields["productversion"]
        sf = self.fields["suites"]
        if self.instance.status == model.Run.STATUS.active:
            # can't change the product version of an active run.
            pvf.queryset = pvf.queryset.filter(
                pk=self.instance.productversion_id)
            pvf.readonly = True
            # can't change suites of an active run either
            sf.readonly = True
        else:
            # regardless, can't switch to different product entirely
            pvf.queryset = pvf.queryset.filter(
                product=self.instance.productversion.product_id)
#            sf.queryset = sf.queryset.filter(
#                product=self.instance.productversion.product_id)

        #@@@ TODO: what does this do?  Does this fetch the included suites?
        # if so, do we still need this?  Perhaps only if run is active/readonly.
        self.initial["suites"] = list(
            self.instance.suites.values_list("id", flat=True))
