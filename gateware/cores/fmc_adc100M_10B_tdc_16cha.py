from artiq.gateware.fmc import _FMC, _fmc_pin
from migen.build.generic_platform import *

from artiq.gateware.rtio.phy.ttl_simple import *
from artiq.gateware.rtio.phy import ttl_serdes_7series
from artiq.gateware.rtio.phy.spi2 import SPIMaster

from misoc.cores import gpio
from artiq.gateware import rtio

from gateware.cores.phy.ads5296a.ads5296a import ADS5296A_XS7
from gateware.cores.phy.tdcgpx2.tdcgpx2 import TdcGpx2Phy

from gateware.cores.daq.adc_daq.adc_phy_daq import AdcPhyDaq
from gateware.cores.daq.tdc_daq.tdcdaq import TdcDaq

from gateware.cores.xilinx import *


class TristateDs(Module):

    def __init__(self, i, o, oe, pads):
        self.specials += Instance("IOBUFDS", i_T=oe, i_I=i, o_O=o, io_IO=pads.p, io_IOB=pads.n)


class FmcAdc100M10b16chaTdc(_FMC):

    @classmethod
    def signal_name(cls, signal_name, fmc):
        return "fmc{}_{}".format(fmc, signal_name)

    @classmethod
    def diff_signal(cls, signal_name, fmc, bank, i, iostd_diff, idx=0):
        return (cls.signal_name(signal_name, fmc), idx,
                Subsignal("p", Pins(_fmc_pin(fmc, bank, i, "p"))),
                Subsignal("n", Pins(_fmc_pin(fmc, bank, i, "n"))),
                IOStandard(iostd_diff["fmc{}_{}".format(fmc, bank)]))

    @classmethod
    def single_signal(cls, signal_name, fmc, bank, i, pol, iostd_single, idx=0):
        return (cls.signal_name(signal_name, fmc), idx, Pins(_fmc_pin(fmc, bank, i, pol)),
                IOStandard(iostd_single["fmc{}_{}".format(fmc, bank)]))

    @classmethod
    def io(cls, fmc, iostd_single, iostd_diff):
        return [
            cls.diff_signal("trig", fmc, "HB", 12, iostd_diff),
            cls.diff_signal("idx_in", fmc, "LA", 32, iostd_diff),

            cls.diff_signal("adc_out_adclk", fmc, "HB", 0, iostd_diff, idx=0),
            cls.diff_signal("adc_out_lclk", fmc, "HB", 6, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out0", fmc, "HB", 2, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out1", fmc, "HB", 9, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out2", fmc, "HB", 8, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out3", fmc, "HB", 3, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out4", fmc, "HB", 5, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out5", fmc, "HB", 7, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out6", fmc, "HB", 4, iostd_diff, idx=0),
            cls.diff_signal("adc_out_out7", fmc, "HB", 1, iostd_diff, idx=0),

            cls.diff_signal("adc_out_adclk", fmc, "HA", 17, iostd_diff, idx=1),
            cls.diff_signal("adc_out_lclk", fmc, "HA", 1, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out0", fmc, "HA", 10, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out1", fmc, "HA", 15, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out2", fmc, "HA", 18, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out3", fmc, "HA", 14, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out4", fmc, "HA", 16, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out5", fmc, "HA", 12, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out6", fmc, "HA", 11, iostd_diff, idx=1),
            cls.diff_signal("adc_out_out7", fmc, "HA", 13, iostd_diff, idx=1),

            cls.diff_signal("tdc_out_lclkout", fmc, "HB", 17, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame0", fmc, "HB", 20, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo0", fmc, "HB", 13, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame1", fmc, "HB", 15, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo1", fmc, "HB", 19, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame2", fmc, "HB", 21, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo2", fmc, "HB", 16, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_frame3", fmc, "HB", 14, iostd_diff, idx=0),
            cls.diff_signal("tdc_out_sdo3", fmc, "HB", 18, iostd_diff, idx=0),

            cls.diff_signal("tdc_out_lclkout", fmc, "LA", 17, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame0", fmc, "LA", 24, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo0", fmc, "LA", 25, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame1", fmc, "LA", 26, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo1", fmc, "LA", 21, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame2", fmc, "LA", 22, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo2", fmc, "LA", 23, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_frame3", fmc, "LA", 19, iostd_diff, idx=1),
            cls.diff_signal("tdc_out_sdo3", fmc, "LA", 20, iostd_diff, idx=1),

            cls.diff_signal("tdc_out_lclkout", fmc, "LA", 0, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame0", fmc, "LA", 9, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo0", fmc, "LA", 7, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame1", fmc, "LA", 8, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo1", fmc, "LA", 5, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame2", fmc, "LA", 6, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo2", fmc, "LA", 4, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_frame3", fmc, "LA", 3, iostd_diff, idx=2),
            cls.diff_signal("tdc_out_sdo3", fmc, "LA", 2, iostd_diff, idx=2),

            cls.diff_signal("tdc_out_lclkout", fmc, "HA", 0, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame0", fmc, "HA", 2, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo0", fmc, "HA", 3, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame1", fmc, "HA", 7, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo1", fmc, "HA", 8, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame2", fmc, "HA", 6, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo2", fmc, "HA", 4, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_frame3", fmc, "HA", 5, iostd_diff, idx=3),
            cls.diff_signal("tdc_out_sdo3", fmc, "HA", 9, iostd_diff, idx=3),

            cls.diff_signal("tdc_dis", fmc, "HB", 10, iostd_diff, idx=0),
            cls.diff_signal("tdc_dis", fmc, "HA", 23, iostd_diff, idx=1),
            cls.diff_signal("tdc_dis", fmc, "LA", 1, iostd_diff, idx=2),
            cls.diff_signal("tdc_dis", fmc, "LA", 10, iostd_diff, idx=3),

            (cls.signal_name("adc_spi", fmc), 0,
             Subsignal("sck", Pins(_fmc_pin(fmc, "HA", 22, "p")), IOStandard(iostd_single["fmc{}_HA".format(fmc)])),
             Subsignal("miso", Pins(_fmc_pin(fmc, "HA", 21, "n")), IOStandard(iostd_single["fmc{}_HA".format(fmc)])),
             Subsignal("mosi", Pins(_fmc_pin(fmc, "LA", 16, "p")), IOStandard(iostd_single["fmc{}_LA".format(fmc)])),
             ),
            cls.single_signal("adc_spi_csn", fmc, "HA", 22, "n", iostd_single, idx=0),
            cls.single_signal("adc_spi_csn", fmc, "LA", 11, "n", iostd_single, idx=1),

            cls.single_signal("adc_resetn", fmc, "LA", 15, "p", iostd_single, idx=0),
            cls.single_signal("adc_sync", fmc, "LA", 30, "p", iostd_single, idx=0),

            (cls.signal_name("tdc_spi", fmc), 0,
             Subsignal("sck", Pins(_fmc_pin(fmc, "LA", 15, "n")), IOStandard(iostd_single["fmc{}_LA".format(fmc)])),
             Subsignal("miso", Pins(_fmc_pin(fmc, "LA", 16, "n")), IOStandard(iostd_single["fmc{}_LA".format(fmc)])),
             Subsignal("mosi", Pins(_fmc_pin(fmc, "LA", 13, "p")), IOStandard(iostd_single["fmc{}_LA".format(fmc)])),
             ),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 31, "n", iostd_single, idx=0),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 31, "p", iostd_single, idx=1),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 12, "p", iostd_single, idx=2),
            cls.single_signal("tdc_spi_csn", fmc, "HA", 20, "n", iostd_single, idx=3),
            cls.single_signal("tdc_spi_csn", fmc, "LA", 14, "n", iostd_single, idx=4),  # CLK CSN

            # TDC INT and TDC PAR are not supported

            cls.single_signal("trig_term", fmc, "LA", 14, "p", iostd_single, idx=0),
            cls.single_signal("trig_dir", fmc, "LA", 13, "n", iostd_single, idx=0),
            cls.single_signal("ref_sel", fmc, "LA", 29, "p", iostd_single, idx=0),
            cls.single_signal("idx_src_sel", fmc, "LA", 30, "n", iostd_single, idx=0),

            # PGOOD is not supported
            # cls.single_signal("pgood", fmc, "LA", 29, "n", iostd_single, idx=0),

            (cls.signal_name("dac_i2c", fmc), 0,
             Subsignal("scl", Pins(_fmc_pin(fmc, "LA", 27, "n")), IOStandard(iostd_single["fmc{}_LA".format(fmc)])),
             Subsignal("sda", Pins(_fmc_pin(fmc, "LA", 27, "p")), IOStandard(iostd_single["fmc{}_LA".format(fmc)])),
             ),

            cls.single_signal("tp35", fmc, "LA", 18, "p", iostd_single, idx=0),
            cls.single_signal("tp36", fmc, "LA", 18, "n", iostd_single, idx=0),
            cls.single_signal("tp37", fmc, "HA", 20, "p", iostd_single, idx=0),
            cls.single_signal("tp38", fmc, "HA", 21, "p", iostd_single, idx=0),
            cls.single_signal("tp39", fmc, "HB", 11, "p", iostd_single, idx=0),
            cls.single_signal("tp40", fmc, "HB", 11, "n", iostd_single, idx=0),
        ]

    @classmethod
    def add_std(cls, target, fmc, iostd_single, iostd_diff, with_trig=False, adc_daq_samples=1024, tdc_daq_samples=1024):
        cls.add_extension(target, fmc, iostd_single, iostd_diff)

        dac_i2c = target.platform.request(cls.signal_name("dac_i2c", fmc))
        target.submodules.i2c = gpio.GPIOTristate([dac_i2c.scl, dac_i2c.sda])
        target.csr_devices.append("i2c")

        for i in range(4):
            pads = target.platform.request(cls.signal_name("tdc_dis", fmc), i)
            phy = Output(pads.p, pads.n)
            target.submodules += phy
            target.add_rtio_channels(rtio.Channel.from_phy(phy), "fmc{}_tdc_dis{} (Output)".format(fmc, i))

        for sn in ["idx_in", "adc_resetn", "adc_sync", "trig_term", "trig_dir", "ref_sel", "idx_src_sel"]:
            pads = target.platform.request(cls.signal_name(sn, fmc), 0)
            if hasattr(pads, "p"):
                phy = Output(pads.p, pads.n)
            else:
                phy = Output(pads)
            target.submodules += phy
            target.add_rtio_channels(rtio.Channel.from_phy(phy), "fmc{}_{} (Output)".format(fmc, sn))

        tdc_spi = target.platform.request(cls.signal_name("tdc_spi", fmc), 0)
        tdc_spi_pads = Signal()
        tdc_spi_pads.clk = tdc_spi.sck
        tdc_spi_pads.miso = tdc_spi.miso
        tdc_spi_pads.mosi = tdc_spi.mosi
        tdc_spi_pads.cs_n = Signal(5)
        # tdc_spi_pads.cs_n = Cat(*[target.platform.request(cls.signal_name("tdc_spi_csn", fmc), i) for i in range(5)])

        phy = SPIMaster(tdc_spi_pads)
        target.submodules += phy
        target.add_rtio_channels(rtio.Channel.from_phy(phy), "fmc{}_tdc_spi (SPIMaster)".format(fmc))

        adc_spi = target.platform.request(cls.signal_name("adc_spi", fmc), 0)
        adc_spi_pads = Signal()
        adc_spi_pads.clk = adc_spi.sck
        adc_spi_pads.miso = adc_spi.miso
        adc_spi_pads.mosi = adc_spi.mosi
        adc_spi_pads.cs_n = Signal(2)
        # adc_spi_pads.cs_n = Cat(*[target.platform.request(cls.signal_name("adc_spi_csn", fmc), i) for i in range(2)])

        phy = SPIMaster(adc_spi_pads)
        target.submodules += phy
        target.add_rtio_channels(rtio.Channel.from_phy(phy), "fmc{}_adc_spi (SPIMaster)".format(fmc))

        # ADC

        for adc_id in range(2):
            # There is single PHY per ADS5296A chip, but each channel has its own DAQ module
            dclk_name = "fmc{}_adc{}_dclk".format(fmc, adc_id)
            phy = ADS5296A_XS7(
                adclk_i=target.platform.request(cls.signal_name("adc_out_adclk", fmc), adc_id),
                lclk_i=target.platform.request(cls.signal_name("adc_out_lclk", fmc), adc_id),
                dat_i=[target.platform.request(cls.signal_name("adc_out_out{}".format(i), fmc), adc_id) for i in range(8)])
            target.platform.add_period_constraint(phy.cd_adclk_clkdiv.clk, 10.)
            phy_renamed_cd = ClockDomainsRenamer({"adclk_clkdiv": dclk_name})(phy)
            setattr(target.submodules, "fmc{}_adc{}_phy".format(fmc, adc_id), phy_renamed_cd)
            target.add_rtio_channels(
                phy.rtio_channels[0],
                "fmc{}_adc{} (ADS5296APhy)".format(fmc, adc_id)
            )

            for channel in range(9):
                daq = ClockDomainsRenamer({"dclk": dclk_name})(AdcPhyDaq(
                    data_clk=phy.data_clk_o,
                    data=phy.data_o[channel],
                    max_samples=adc_daq_samples))
                setattr(target.submodules, "fmc{}_adc{}_daq{}".format(fmc, adc_id, channel), daq)
                target.add_rtio_channels(
                    rtio.Channel.from_phy(daq),
                    "fmc{}_adc{}_daq{} (AdcPhyDaq)".format(fmc, adc_id, channel))

        # TDC

        for tdc_id in range(4):
            dclk_name = "fmc{}_tdc{}_dclk".format(fmc, tdc_id)
            fs = [target.platform.request(cls.signal_name("tdc_out_frame{}".format(i), fmc), tdc_id) for i in range(4)]
            ds = [target.platform.request(cls.signal_name("tdc_out_sdo{}".format(i), fmc), tdc_id) for i in range(4)]
            phy = TdcGpx2Phy(data_clk_i=target.platform.request(cls.signal_name("tdc_out_lclkout", fmc), tdc_id),
                             frame_signals_i=fs,
                             data_signals_i=ds)
            target.platform.add_period_constraint(phy.cd_dclk.clk, 4.)
            phy_renamed_cd = ClockDomainsRenamer({"dclk": dclk_name})(phy)
            setattr(target.submodules, "fmc{}_tdc{}_phy".format(fmc, tdc_id), phy_renamed_cd)
            target.add_rtio_channels(
                phy.rtio_channels,
                ["fmc{}_tdc{}_phy_ch{} (TdcGpx2PhyChannel)".format(fmc, tdc_id, ch) for ch in range(4)])

            for channel in range(4):
                daq = TdcDaq(data_i=phy.data_o[channel],
                             stb_i=phy.data_stb_o[channel],
                             channel_depth=tdc_daq_samples)
                daq_renamed = ClockDomainsRenamer({"dclk": dclk_name})(daq)
                setattr(target.submodules, "fmc{}_tdc{}_daq{}".format(fmc, tdc_id, channel), daq_renamed)
                target.add_rtio_channels(daq.rtlink_channels,
                                         ["fmc{}_tdc{}_daq{}_msb (TdcDaq)".format(fmc, tdc_id, channel),
                                          "fmc{}_tdc{}_daq{}_lsb (TdcDaq)".format(fmc, tdc_id, channel)])

        csn_pads = [
            *[target.platform.request(cls.signal_name("tdc_spi_csn", fmc), i) for i in range(5)],
            *[target.platform.request(cls.signal_name("adc_spi_csn", fmc), i) for i in range(2)]
        ]

        for i, pad in enumerate(csn_pads):
            phy = Output(pad)
            target.submodules += phy
            target.add_rtio_channels(rtio.Channel.from_phy(phy), "fmc{}_csn{} (Output)".format(fmc, i))

        if with_trig:
            pads = target.platform.request(cls.signal_name("trig", fmc))
            phy = ttl_serdes_7series.InOut_8X(pads.p, pads.n)
            target.submodules += phy
            target.add_rtio_channels(rtio.Channel.from_phy(phy, ififo_depth=64), "fmc{}_trig (InOut_8X)".format(fmc))
