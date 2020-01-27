from artiq.coredevice import spi2 as spi
from artiq.coredevice.ttl import TTLInOut, TTLOut
from artiq.language.units import ns, us
from coredevice.ad9528 import AD9528
from coredevice.ad9528_default_config import AD9528_DEFAULT_CONFIG
from coredevice.ads5296a import ADS5296A
from coredevice.tdc_gpx2 import TDCGPX2
from artiq.language.core import kernel


class FmcAdc100M10bTdc16cha:

    def __init__(self, dmgr, channel, with_trig, core_device="core"):
        self.channel = channel
        self.core = dmgr.get(core_device)
        self.ref_period_mu = self.core.seconds_to_mu(
            self.core.coarse_ref_period)

        self.tdc_disable = [
            TTLOut(dmgr, self.channel + i, core_device) for i in range(4)
        ]

        self.idx_in = TTLOut(dmgr, self.channel + 4, core_device)
        self.adc_resetn = TTLOut(dmgr, self.channel + 5, core_device)
        self.adc_sync = TTLOut(dmgr, self.channel + 6, core_device)
        self.trig_term = TTLOut(dmgr, self.channel + 7, core_device)
        self.trig_dir = TTLOut(dmgr, self.channel + 8, core_device)
        self.ref_sel = TTLOut(dmgr, self.channel + 9, core_device)
        self.idx_src_sel = TTLOut(dmgr, self.channel + 10, core_device)

        self.adc_spi = spi.SPIMaster(dmgr, self.channel + 12, core_device=core_device)
        self.tdc_spi = spi.SPIMaster(dmgr, self.channel + 11, core_device=core_device)

        self.tdc_csn = [TTLOut(dmgr, self.channel + 79 + i, core_device) for i in range(4)]
        self.clock_csn = TTLOut(dmgr, self.channel + 79 + 4, core_device)
        self.adc_csn = [TTLOut(dmgr, self.channel + 79 + 5 + i, core_device) for i in range(2)]

        self.adc = [
            ADS5296A(dmgr, self.channel + 13 + i*9, self.adc_spi, self.adc_csn[i], core_device=core_device, spi_freq=500_000) for i in range(2)
        ]
        self.tdc = [
            TDCGPX2(dmgr, self.channel + 31 + i*12, self.tdc_spi, self.tdc_csn[i], core_device=core_device, spi_freq=500_000) for i in range(4)
        ]

        if with_trig:
            self.trig = TTLInOut(dmgr, channel + 86, core_device)

        self.clock = AD9528(dmgr=dmgr,
                            spi_device=self.tdc_spi,
                            chip_select=self.clock_csn,
                            spi_freq=10_000_000,
                            config=AD9528_DEFAULT_CONFIG,
                            core_device=core_device)

    @kernel
    def deactivate_all_spi_devices(self):
        self.core.break_realtime()
        for ttl in self.tdc_csn:
            ttl.on()
        self.clock_csn.on()
        for ttl in self.adc_csn:
            ttl.on()

    @kernel
    def reset_ad9528_and_adc(self):
        self.core.break_realtime()
        self.adc_resetn.off()
        delay(1*us)
        self.adc_resetn.on()

    def initialize(self):
        self.deactivate_all_spi_devices()
        self.reset_ad9528_and_adc()
        self.clock.initialize()
