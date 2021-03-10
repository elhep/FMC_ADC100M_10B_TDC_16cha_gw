from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *


from migen import *
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer, ElasticBuffer, MultiReg
from migen.genlib.fifo import AsyncFIFO, AsyncFIFOBuffered
from migen.fhdl import verilog
from artiq.gateware.rtio import rtlink, Channel

from functools import reduce
from operator import and_

from cores.daq.circular_buffer import CircularBuffer


class TdcDaq(Module):

    """
    TDC DAQ uses circular buffer to store time stamps from the TDC.
    To make trigger-driven gating easier, position of the circular
    buffer is advanced with every clock cycle. As this clock is of
    the same frequency as ADC clock we can assume that given pretrigger
    samples number will give us the same time range both for TDC and
    ADC DAQ.

    We're assuming that data output from the TDC will not be longer
    than 32-trigger_cnt_len (to fit in single rtlink channel).

    Trigger is assummed to be in DCLK domain!
    """

    def __init__(self, data_i, stb_i, trigger_rio_phy, 
        circular_buffer_length=128, channel_depth=128, trigger_cnt_len=4):

        # This module does not expose interface for combinatorial connection
        # Signals are passed during initialization.
        # Module provides RTIO channels.

        # RTLink map address:
        # 0: pretrigger
        # 1: posttrigger
        # There is no readout for configuration values!
        
        # # #

        data_width = len(data_i)
        assert data_width <= 32-trigger_cnt_len

        pretrigger_rio_phy = Signal(max=circular_buffer_length)
        posttrigger_rio_phy = Signal.like(pretrigger_rio_phy)
        pretrigger_dclk = Signal.like(pretrigger_rio_phy)
        posttrigger_dclk = Signal.like(posttrigger_rio_phy)
        trigger_dclk = Signal()

        # Interface - rtlink
        self.rtlink = rtlink_iface = rtlink.Interface(
            rtlink.OInterface(data_width=len(pretrigger_rio_phy), address_width=2),
            rtlink.IInterface(data_width=data_width+trigger_cnt_len, timestamped=True))
        self.rtlink_channels = [Channel(rtlink_iface, ififo_depth=channel_depth)]

        self.sync.rio_phy += [
            If(rtlink_iface.o.stb,
               If(self.rtlink.o.address == 0, pretrigger_rio_phy.eq(rtlink_iface.o.data)),
               If(self.rtlink.o.address == 1, posttrigger_rio_phy.eq(rtlink_iface.o.data)),
            )
        ]

        trigger_cnt = Signal(trigger_cnt_len, reset=0)
        trigger_d = Signal()

        self.sync.dclk += [
            If(trigger_dclk & ~trigger_d,  # detect trigger re
                trigger_cnt.eq(trigger_cnt+1)),
            trigger_d.eq(trigger_dclk)
        ]

        # Data format (MSb first):
        # <tdc_data, 22b>
        # <trigger_cnt, trigger_cnt_len>
        # <data valid, 1b>

        cb_data_in = Signal(data_width+1)
        self.comb += [
            cb_data_in.eq(Cat(stb_i, trigger_cnt, data_i))
        ]

        circular_buffer = ClockDomainsRenamer({"sys": "dclk"})(CircularBuffer(data_width+1, circular_buffer_length))
        async_fifo = ClockDomainsRenamer({"write": "dclk", "read": "rio_phy"})(AsyncFIFOBuffered(data_width+1, 16))
        trigger_cdc = PulseSynchronizer("rio_phy", "dclk")
        pretrigger_cdc = MultiReg(pretrigger_rio_phy, pretrigger_dclk, "dclk")
        posttrigger_cdc = MultiReg(posttrigger_rio_phy, posttrigger_dclk, "dclk")
        self.submodules += [circular_buffer, async_fifo, trigger_cdc]
        self.specials += [pretrigger_cdc, posttrigger_cdc]

        self.comb += [
            trigger_cdc.i.eq(trigger_rio_phy),
            trigger_dclk.eq(trigger_cdc.o),
            circular_buffer.data_in.eq(cb_data_in),
            circular_buffer.we.eq(1),
            circular_buffer.trigger.eq(trigger_dclk),
            circular_buffer.pretrigger.eq(pretrigger_dclk),
            circular_buffer.posttrigger.eq(posttrigger_dclk),
            async_fifo.din.eq(circular_buffer.data_out),
            async_fifo.re.eq(async_fifo.readable),
            async_fifo.we.eq(circular_buffer.stb_out),
            rtlink_iface.i.data.eq(async_fifo.dout[1:]),  # two LSb are data valid (TDC frame)
            rtlink_iface.i.stb.eq(reduce(and_, [async_fifo.dout[0], async_fifo.readable]))  # stb if there are data and frame
        ]


class SimulationWrapper(Module):

    def __init__(self):

        data_width = 22

        data_i = Signal(bits_sign=data_width, name="data_i")
        stb_i  = Signal(name="data_stb_i")
        trigger_rio_phy = Signal(name="trigger")

        self.data_clk = Signal(name="dclk_clk")

        self.clock_domains.cd_rio_phy = cd_rio_phy = ClockDomain()
        self.clock_domains.cd_dclk = cd_dclk = ClockDomain()

        self.comb += [cd_dclk.clk.eq(self.data_clk)]

        self.submodules.dut = dut = TdcDaq(
            data_i=data_i, 
            stb_i=stb_i,
            trigger_rio_phy=trigger_rio_phy,
            circular_buffer_length=128,
            channel_depth=128,
            trigger_cnt_len=4)

        dut.rtlink_channels[0].interface.o.stb.name_override = "rtlink_stb_i"
        dut.rtlink_channels[0].interface.o.address.name_override = "rtlink_adr_i"
        dut.rtlink_channels[0].interface.o.data.name_override = "rtlink_data_i"

        dut.rtlink_channels[0].interface.i.stb.name_override = "rtlink_stb_o"
        dut.rtlink_channels[0].interface.i.data.name_override = "rtlink_data_o"

        self.io = {
            cd_dclk.clk,
            cd_dclk.rst,

            data_i,
            stb_i,
            trigger_rio_phy,

            cd_rio_phy.clk,
            cd_rio_phy.rst,

            dut.rtlink_channels[0].interface.o.stb,
            dut.rtlink_channels[0].interface.o.address,
            dut.rtlink_channels[0].interface.o.data,

            dut.rtlink_channels[0].interface.i.stb,
            dut.rtlink_channels[0].interface.i.data
        }


if __name__ == "__main__":

    from migen.build.xilinx import common
    from gateware.simulation.common import update_tb

    module = SimulationWrapper()
    so = dict(common.xilinx_special_overrides)
    so.update(common.xilinx_s7_special_overrides)

    verilog.convert(fi=module,
                    name="top",
                    special_overrides=so,
                    ios=module.io,
                    create_clock_domains=False).write('tdc_gpx2_daq.v')
    update_tb('tdc_gpx2_daq.v')
