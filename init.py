"""Raumheizungssteuerung Integration."""
from homeassistant.core import HomeAssistant
from .coordinator import HeizungsCoordinator

DOMAIN = "raumheizungssteuerung"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up from a config entry."""
    coordinator = HeizungsCoordinator(hass, entry)
    await coordinator.async_start()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_stop()
    return True
