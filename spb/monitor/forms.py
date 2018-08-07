from django import forms
from api.models import Pump


class LoginForm(forms.Form):
    """
    Form for the Login page
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom:10px;'}),
        required=True,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
    )


class PumpModelForm(forms.ModelForm):
    """
    Model form class for the pump model class
    """

    active = forms.BooleanField(
        required=False,
        label='Active',
        widget=forms.Select(
            choices=[
                (True, 'Yes'),
                (False, 'No')
            ]
        ),
        initial=True,
    )
    name = forms.CharField(
        label='Name',
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(
            attrs={
                'rows': 2,
            }
        ),
        required=False,
    )
    sleepTime = forms.IntegerField(
        label='Sleep Time [s]',
        initial=24 * 60 * 60,
        min_value=0,
    )
    activeTime = forms.IntegerField(
        label='Active Time [s]',
        initial=10,
        min_value=0
    )
    remainingContainerVolume = forms.FloatField(
        label='Remain Water Container Volume [l]',
        initial=2.0,
        min_value=0,
        required=False,
    )
    maxContainerVolume = forms.FloatField(
        label='Max Water Container Volume [l]',
        initial=2.0,
        min_value=0,
        required=False,
    )
    throughput = forms.FloatField(
        label='Water Throughput [l/s]',
        initial=1.0,
        min_value=0,
        required=False,
    )
    power = forms.FloatField(
        label='Electrical Pump Power [W]',
        initial='10',
        min_value=0,
        required=False,
    )
    remainingBatteryCapacity = forms.IntegerField(
        label='Remaining Battery Capacity [mAh]',
        initial=1000,
        min_value=0,
        required=False,
    )
    maxBatteryCapacity = forms.IntegerField(
        label='Max Battery Capacity [mAh]',
        initial=1000,
        min_value=0,
        required=False,
    )
    operatingVoltage = forms.FloatField(
        label='Operating Voltage [V]',
        initial=3.3,
        min_value=0,
    )
    needsService = forms.BooleanField(
        required=False,
        label='Service Required',
        widget=forms.Select(
            choices=[
                (True, 'Yes'),
                (False, 'No')
            ]
        ),
        initial=False,
    )

    class Meta:
        model = Pump
        fields = ('name', 'description', 'active', 'sleepTime', 'activeTime', "maxContainerVolume",
                  "remainingContainerVolume",
                  'maxBatteryCapacity', 'remainingBatteryCapacity', 'power', 'throughput', 'operatingVoltage',
                  'needsService')

    def is_valid(self):
        """
        Method checks if the form data is valid

        :return: True if the data is valid else False
        """
        if not super(PumpModelForm, self).is_valid():
            return False

        remaining_vol = self.cleaned_data['remainingContainerVolume']
        max_vol = self.cleaned_data['maxContainerVolume']
        remaining_battery = self.cleaned_data['remainingBatteryCapacity']
        max_battery = self.cleaned_data['maxBatteryCapacity']

        if (remaining_vol is not None and max_vol is not None) and remaining_vol > max_vol:
            self._errors['remainingContainerVolume'] = [
                'Remaining container volume can not be greater than maximum container volume'
            ]
            return False
        elif remaining_vol is None and max_vol is not None:
            self._errors['remainingContainerVolume'] = [
                'Remaining water volume can not be empty when a value for the maximum container volume is set'
            ]
            return False
        elif remaining_vol is not None and max_vol is None:
            self._errors['maxContainerVolume'] = [
                'Maximum container volume can not be empty when a value for the remaining container volume is set'
            ]
            return False

        if (remaining_battery is not None and max_battery is not None) and remaining_battery > max_battery:
            self._errors['remainingBatteryCapacity'] = [
                'Remaining battery capacity can not be greater than maximum battery capacity'
            ]
            return False
        elif remaining_battery is None and max_battery is not None:
            self._errors['remainingBatteryCapacity'] = [
                'Remaining battery capacity can not be empty when a value for the maximum battery capacity is set'
            ]
            return False
        elif remaining_battery is not None and max_battery is None:
            self._errors['maxBatteryCapacity'] = [
                'Maximum battery capacity can not be empty when a value for the remaining battery capacity is set'
            ]
            return False

        return True
