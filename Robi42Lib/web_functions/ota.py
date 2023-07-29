import time
import json
import network
import urequests


class OTAUpdate():
    artifact_url = r'https://git.ebg-vaterstetten.de/api/v4/projects/roboter_internal%2FPythonPrototypLib/jobs/artifacts/{branch}/raw/{file}?job=build'
    branch = 'master'
    ota_package = 'artifacts.tar'
    meta_package = 'meta.json'
    access_token = 'glpat-67QiEkappj-Ycnz4EpPB'

    def __init__(self):
        self.connect_wlan('DARC', 'darcovc01')
        time.sleep(5)
        self.ota_metadata = self._fetch_metadata()

    def connect_wlan(self, ssid: str, password: str):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)

    def _fetch_metadata(self) -> dict:
        url = self.artifact_url.format(
            branch=self.branch,
            file=self.meta_package,
        )
        response = urequests.get(url, headers={'PRIVATE-TOKEN': self.access_token})
        if response.status_code != 200:
            raise RuntimeError('Cannot find current version on server. -> {}'.format(response.status_code))
        data = response.json()
        return data
    
    def is_update_available():
        ...


ota = OTAUpdate()
