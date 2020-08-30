"""
Module for exposing a (virtual) sensor to KNX bus.

It provides functionality for

* push local state changes to KNX bus
* KNX devices may read local values via GROUP READ.

(A typical example for using this class is the outside temperature
read from an internet service (e.g. Yahoo weather) and exposed to
ths KNX bus. KNX sensors may show this outside temperature within their
LCD display.
"""
from xknx.remote_value import RemoteValueSensor, RemoteValueSwitch

from .device import Device


class ExposeSensor(Device):
    """Class for managing a sensor."""

    def __init__(
        self, xknx, name, group_address=None, value_type=None, device_updated_cb=None
    ):
        """Initialize Sensor class."""
        # pylint: disable=too-many-arguments
        super().__init__(xknx, name, device_updated_cb)

        self.sensor_value = None
        if value_type == "binary":
            self.sensor_value = RemoteValueSwitch(
                xknx,
                group_address=group_address,
                sync_state=False,
                device_name=self.name,
                after_update_cb=self.after_update,
            )
        else:
            self.sensor_value = RemoteValueSensor(
                xknx,
                group_address=group_address,
                sync_state=False,
                device_name=self.name,
                after_update_cb=self.after_update,
                value_type=value_type,
            )

    def _iter_remote_values(self):
        """Iterate the devices RemoteValue classes."""
        yield self.sensor_value

    @classmethod
    def from_config(cls, xknx, name, config):
        """Initialize object from configuration structure."""
        group_address = config.get("group_address")
        value_type = config.get("value_type")

        return cls(xknx, name, group_address=group_address, value_type=value_type)

    async def process_group_read(self, telegram):
        """Process incoming GROUP READ telegram."""
        await self.sensor_value.send(response=True)

    async def set(self, value):
        """Set new value."""
        await self.sensor_value.set(value)

    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.sensor_value.unit_of_measurement

    def resolve_state(self):
        """Return the current state of the sensor as a human readable string."""
        return self.sensor_value.value

    def __str__(self):
        """Return object as readable string."""
        return '<ExposeSensor name="{}" ' 'sensor="{}" value="{}" unit="{}"/>'.format(
            self.name,
            self.sensor_value.group_addr_str(),
            self.resolve_state(),
            self.unit_of_measurement(),
        )
