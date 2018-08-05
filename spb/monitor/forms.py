from django import forms
from api.models import Pump


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
    )
    maxContainerVolume = forms.FloatField(
        label='Max Water Container Volume [l]',
        initial=2.0,
        min_value=0,
    )
    throughput = forms.FloatField(
        label='Water Throughput [l/s]',
        initial=1.0,
        min_value=0,
    )
    power = forms.FloatField(
        label='Electrical Pump Power [W]',
        initial='10',
        min_value=0,
    )
    remainingBatteryCapacity = forms.IntegerField(
        label='Remaining Battery Capacity [mAh]',
        initial=1000,
        min_value=0,
    )
    maxBatteryCapacity = forms.IntegerField(
        label='Max Battery Capacity [mAh]',
        initial=1000,
        min_value=0,
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

        if self.cleaned_data["remainingContainerVolume"] > self.cleaned_data["maxContainerVolume"]:
            self._errors['remainingContainerVolume'] = [
                'Remaining water volume can not be greater than maximal water volume']
            return False

        if self.cleaned_data['remainingBatteryCapacity'] > self.cleaned_data['maxBatteryCapacity']:
            self._errors['remainingBatteryCapacity'] = ['Remaining capacity can not be greater than maximal capacity']
            return False

        return True
