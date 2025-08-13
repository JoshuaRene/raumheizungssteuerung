from homeassistant.helpers.event import async_track_time_interval
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class HeizungsCoordinator:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._unsub = None
        self.last_antikalk = None

    async def async_start(self):
        """Start periodic updates every 5 minutes."""
        self._unsub = async_track_time_interval(
            self.hass, self.update_heizung, timedelta(minutes=5)
        )

    async def async_stop(self):
        """Stop periodic updates."""
        if self._unsub:
            self._unsub()
            self._unsub = None

    async def update_heizung(self, now):
        """Check each room and adjust temperature."""
        data = self.entry.data.get("raeume", [])
        sommermodus = self.entry.data.get("sommermodus", False)
        aussentemp = float(self.hass.states.get("sensor.aussentemperatur").state)

        today = datetime.now().date()
        if self.last_antikalk == today:
            anti_kalk_gemacht = True
        else:
            anti_kalk_gemacht = False

        for raum in data:
            heizkoerper = raum.get("heizkoerper")
            fenster = raum.get("fenster", [])
            temp = float(raum.get("ziel_temp", 21))
            nachtabsenkung = raum.get("nachtabsenkung", {})

            # Nachtabsenkung prüfen
            stunde = datetime.now().hour
            if nachtabsenkung.get("aktiv", False):
                start = nachtabsenkung.get("start", 22)
                ende = nachtabsenkung.get("ende", 6)
                nacht_temp = nachtabsenkung.get("temp", 18)
                if start <= stunde or stunde < ende:
                    temp = nacht_temp

            # Fenster offen prüfen
            fenster_offen = any(self.hass.states.get(f).state == "on" for f in fenster)

            if sommermodus and aussentemp > 20:
                if not anti_kalk_gemacht:
                    await self.set_temp(heizkoerper, 30)
                    _LOGGER.info(f"[{raum['name']}] Sommermodus Anti-Kalk gestartet")
                    await self.set_temp(heizkoerper, 5)
                    self.last_antikalk = today
            elif fenster_offen:
                await self.set_temp(heizkoerper, 5)
            else:
                await self.set_temp(heizkoerper, temp)

    async def set_temp(self, entity_id, temp):
        self.hass.services.call("climate", "set_temperature", {
            "entity_id": entity_id,
            "temperature": temp
        })
