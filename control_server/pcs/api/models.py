from django.contrib.auth.models import User
from django.db import models
from pcs.settings import LOW_RESOURCE_THRESHHOLD

LOW_BATTERY_SERVICE_TASK = 'Recharge/Replace Battery'
LOW_WATER_SERVICE_TASK = 'Refill Water'


class Pump(models.Model):
    """
    Model class for ESP controlled pumps
    """

    # Bool flag for the indication if the pump is activated or is in stand by
    active = models.BooleanField(default=True)
    # Standby time in seconds
    sleepTime = models.PositiveIntegerField(default=12 * 60 * 60)
    # Pump time in seconds
    activeTime = models.PositiveIntegerField(default=2)
    # Description
    description = models.TextField(null=True, blank=True)
    # Name of this pump
    name = models.CharField(blank=False, null=False, max_length=200, unique=True)
    # Timestamp of the last request
    lastRequest = models.DateTimeField(auto_now=True)
    # Remaining volume of the water tank in liters
    remainingTankVolume = models.FloatField(null=True)
    # Max volume of the water tank in liters
    maxTankVolume = models.FloatField(null=True)
    # Throughput of this pump in liters per second
    throughput = models.FloatField(null=True)
    # Electrical power of the pump in Watts
    power = models.FloatField(null=True)
    # Remaining capacity of the battery in mAh
    remainingBatteryCapacity = models.PositiveIntegerField(default=0, null=True)
    # Max capacity of the battery in mAh
    maxBatteryCapacity = models.PositiveIntegerField(default=0, null=True)
    # Operating voltage of the pump
    operatingVoltage = models.FloatField(null=True)
    # Bool flag for the indication if refilling of water or recharging of the battery is necessary
    needsService = models.BooleanField(default=False)
    # foreign key to the owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)

    def update_capacity(self, active):
        """
        This method does a rough estimation of the remaining battery and water capacity based on the provided value
        for the parameter active and updates values of the attributes remainingBatteryCapacity and remainingTankVolume

        :param active: Amount of time in which the pump pumps
        :type active: int
        :return: None
        """

        if self.remainingBatteryCapacity is not None:
            # rough estimation of the remaining battery and water capacity
            # calculate energy consumption of the pump
            # 5/18 = 1000/3600 = conversion factor from As to mAh
            self.remainingBatteryCapacity -= ((self.power * active) / self.operatingVoltage) * (5 / 18)
            # calculate energy consumption of the ESP during the request and active time
            self.remainingBatteryCapacity += 0.1 * (active + 4) * (5 / 18)
        if self.remainingTankVolume is not None:
            # calculate amount of pumped water
            self.remainingTankVolume -= self.throughput * active
        # update status values
        self.save()

    def health_check(self):
        """
        Method checks if the amount of the remaining water and battery capacity is higher then the configured threshold
        value. If the value is lower an instance of ServiceTask class gets created with a description of the requiered
        task.

        :return: True if no service is requiered else False
        :rtype: bool
        """

        if self.remainingBatteryCapacity is not None and \
                        self.remainingBatteryCapacity <= self.maxBatteryCapacity * LOW_RESOURCE_THRESHHOLD:
            self.needsService = True
            ServiceTask.objects.create(pump=self, task=LOW_BATTERY_SERVICE_TASK)
        if self.remainingTankVolume is not None and \
                        self.remainingTankVolume <= self.maxTankVolume * LOW_RESOURCE_THRESHHOLD:
            self.needsService = True
            ServiceTask.objects.create(pump=self, task=LOW_WATER_SERVICE_TASK)
        self.save()
        return not self.needsService


class TransmittedTiming(models.Model):
    """
    Model class for the logging of the sent timing values
    """

    pump = models.ForeignKey(Pump, on_delete=models.CASCADE)
    # Sent standby time in seconds
    sleepTime = models.PositiveIntegerField()
    # Sent pump time in seconds
    activeTime = models.PositiveIntegerField()
    # Timestamp of this log entry
    timeStamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.timeStamp, str(self.pump))


class ServiceTask(models.Model):
    """
    Model class for the storage of the requiered service tasks for a pump
    """

    pump = models.ForeignKey(Pump, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)

    def __str__(self):
        return '{}:{}'.format(str(self.pump), self.task)
