from django_tables2 import Table, tables
from api.models import Pump


class PumpTable(Table):
    """
    Table for the listing of the registered pumps
    """

    class Meta:
        model = Pump
        attrs = {
            'class': 'table table-borderless table-hover'
        }
        fields = ('name', 'state', 'remainingTankVolume', 'remainingBatteryCapacity', 'lastRequest', 'details', 'delete')

    name = tables.columns.Column(verbose_name='Name')
    state = tables.columns.TemplateColumn("""
    {% if record.needsService and record.active %}
        <button type="button" class="btn btn-warning">Service Required</button>
    {% else %}
            {% if record.active %}
                <button type="button" class="btn btn-success">Active</button>
            {% else %}
                <button type="button" class="btn btn-secondary">Deactivated</button>
            {% endif %}
    {% endif %}
    """)
    remainingTankVolume = tables.columns.Column(verbose_name='Remaining Water [l]')
    remainingBatteryCapacity = tables.columns.Column(verbose_name='Remaining Battery [mAh]')
    lastRequest = tables.columns.DateTimeColumn(verbose_name='Last Request')
    details =  tables.columns.TemplateColumn(
        '<a href="{% url "monitor:pump_details" record.id %}"><button type="button" class="btn btn-info">Details</button></a>',
        verbose_name=''
    )
    delete = tables.columns.TemplateColumn(
        '<button type="button" class="btn btn-danger" onclick="delete_and_reload(\'{% url "monitor:pump_details" record.id %}\')">Delete</button>',
        verbose_name=''
    )
