from django import forms
from .models import Role, Module, RoleModuleAccess
from django.db.models import Case, When, Value, CharField

class RoleAdminForm(forms.ModelForm):
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'module-checkbox-grid'
        }),
        required=False
    )

    class Meta:
        model = Role
        fields = ['sn','h_name','name', 'modules']

    def __init__(self, *args, **kwargs):
        super(RoleAdminForm, self).__init__(*args, **kwargs)

        self.fields['modules'].queryset = Module.objects.annotate(
            suffix=Case(
                When(name__endswith='_admin', then=Value('admin')),
                When(name__endswith='_battalion', then=Value('battalion')),
                When(name__endswith='_company', then=Value('company')),
                When(name__endswith='_member', then=Value('member')),
                default=Value('zzz'),
                output_field=CharField()
            )
        ).order_by('suffix','id')

    def save(self, commit=True):
        role = super().save(commit=False)
        if commit:
            role.save()
            self.save_m2m()
        return role

    def save_m2m(self):
        modules = self.cleaned_data['modules']
        self.instance.modules.clear()
        for module in modules:
            RoleModuleAccess.objects.get_or_create(role=self.instance, module=module)




