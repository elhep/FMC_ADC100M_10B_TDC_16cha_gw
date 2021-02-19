from migen.build.xilinx.platform import XilinxPlatform
from migen.build.generic_platform import *


from migen import *
from migen.fhdl.specials import Memory
from migen.genlib.cdc import BusSynchronizer, PulseSynchronizer
from migen.fhdl import verilog
from artiq.gateware.rtio import rtlink


class AdcPhyDaq(Module):

    def __init__(self, data_clk, data, max_samples):

        """
        Output:
          0: trigger
          1: pretrigger[23:12], posttrigger[11:0]
        """

        # --------------------------------------------------------------------------------------------------------------
        # Sample memory

        assert max_samples <= 2**12-1

        memory = Memory(len(data), max_samples, init=[0]*max_samples)
        memory_write_port = memory.get_port(write_capable=True, clock_domain="dclk")
        memory_read_port = memory.get_port(has_re=True, clock_domain="rio_phy")
        self.specials += [ memory, memory_write_port, memory_read_port ]

        # --------------------------------------------------------------------------------------------------------------
        # Data clock domain

        trigger_dclk = Signal()
        trigger_dclk.attr.add(("mark_debug", "true"))
        pretrigger_len_dclk = Signal(12, reset=16)
        posttrigger_len_dclk = Signal(12, reset=16)

        current_address_dclk = Signal.like(memory_write_port.adr, reset=0)
        current_address_dclk.attr.add(("mark_debug", "true"))
        data_start_address_dclk = Signal.like(current_address_dclk)
        data_start_address_reg_dclk = Signal.like(data_start_address_dclk)
        trig_prev_dclk = Signal()
        trig_re_dclk = Signal()
        posttrigger_counter_dclk = Signal(max=max_samples)
        transfer_en_dclk = Signal()
        transfer_done_dclk = Signal()

        self.sync.dclk += [
            # We need to wrap current_address when buffer_depth is reached
            If(current_address_dclk == max_samples-1,
               current_address_dclk.eq(0))
            .Else(
               current_address_dclk.eq(current_address_dclk+1)),

            # We'll be using rising edge of trig, previous value is needed
            trig_prev_dclk.eq(trigger_dclk)
        ]

        self.comb += [
            memory_write_port.adr.eq(current_address_dclk),
            memory_write_port.dat_w.eq(data),
            trig_re_dclk.eq(trigger_dclk & ~trig_prev_dclk),
            # Compute start address for further readout
            If(current_address_dclk < pretrigger_len_dclk,
                data_start_address_dclk.eq(max_samples + current_address_dclk - pretrigger_len_dclk)).
            Else(
                data_start_address_dclk.eq(current_address_dclk - pretrigger_len_dclk)),
        ]

        # Data clock side FSM
        fsm_dclk = ClockDomainsRenamer("dclk")(FSM("PRETRIGGER"))
        fsm_dclk.act("PRETRIGGER",
                memory_write_port.we.eq(1),
                If(trig_re_dclk,
                   NextValue(data_start_address_reg_dclk, data_start_address_dclk),
                   If(posttrigger_len_dclk != 0,
                       NextValue(posttrigger_counter_dclk, posttrigger_len_dclk),
                       NextState("POSTTRIGGER")).
                   Else(
                       NextState("TRANSFER"),
                       NextValue(transfer_en_dclk, 1))
                ))
        fsm_dclk.act("POSTTRIGGER",
                memory_write_port.we.eq(1),
                NextValue(posttrigger_counter_dclk, posttrigger_counter_dclk-1),
                If(posttrigger_counter_dclk == 0,
                   NextState("TRANSFER"),
                   NextValue(transfer_en_dclk, 1))
                )
        fsm_dclk.act("TRANSFER",
                memory_write_port.we.eq(0),
                NextValue(transfer_en_dclk, 0),
                If(transfer_done_dclk,
                   NextState("PRETRIGGER"))
                )
        self.submodules.fsm_dclk = fsm_dclk
        
        # --------------------------------------------------------------------------------------------------------------
        # RIO Clock Domain

        self.rtlink = rtlink.Interface(
            rtlink.OInterface(data_width=24, address_width=2),  # address_width = width + 1
            rtlink.IInterface(data_width=10, timestamped=True))

        # self.rtlink.o.stb.attr.add(("mark_debug", "true"))
        # self.rtlink.o.address.attr.add(("mark_debug", "true"))
        # self.rtlink.o.data.attr.add(("mark_debug", "true"))
        # self.rtlink.i.data.attr.add(("mark_debug", "true"))
        # self.rtlink.i.stb.attr.add(("mark_debug", "true"))

        # memory_read_port.adr.attr.add(("mark_debug", "true"))
        # memory_read_port.dat_r.attr.add(("mark_debug", "true"))
        # memory_read_port.re.attr.add(("mark_debug", "true"))

        # memory_write_port.adr.attr.add(("mark_debug", "true"))
        # memory_write_port.dat_w.attr.add(("mark_debug", "true"))
        # memory_write_port.we.attr.add(("mark_debug", "true"))

        trigger_rio_phy = Signal()
        # trigger_rio_phy.attr.add(("mark_debug", "true"))
        pretrigger_len_rio_phy = Signal.like(pretrigger_len_dclk)
        posttrigger_len_rio_phy = Signal.like(posttrigger_counter_dclk)
        transfer_done_rio_phy = Signal()
        # transfer_done_rio_phy.attr.add(("mark_debug", "true"))

        data_start_address_reg_rio_phy = Signal.like(data_start_address_reg_dclk)
        transfer_en_rio_phy = Signal()
        # transfer_en_rio_phy.attr.add(("mark_debug", "true"))

        counter_rio_phy = Signal.like(memory_read_port.adr)

        # Rio clock side FSM
        fsm_rio_phy = ClockDomainsRenamer("rio_phy")(FSM("IDLE"))
        fsm_rio_phy.act("IDLE",
                memory_read_port.re.eq(0),
                NextValue(transfer_done_rio_phy, 0),
                NextValue(self.rtlink.i.stb, 0),
                If(transfer_en_rio_phy,
                   NextValue(memory_read_port.adr, data_start_address_reg_rio_phy),
                   NextValue(counter_rio_phy, 0),
                   NextState("TRANSFER"))
                )
        fsm_rio_phy.act("TRANSFER",
                memory_read_port.re.eq(1),
                NextValue(counter_rio_phy, counter_rio_phy+1),
                NextValue(self.rtlink.i.stb, 1),
                If(memory_read_port.adr+1 >= max_samples,
                   NextValue(memory_read_port.adr, 0))
                .Else(NextValue(memory_read_port.adr, memory_read_port.adr+1)),
                If(counter_rio_phy == (pretrigger_len_rio_phy + posttrigger_len_rio_phy - 1),
                   NextState("IDLE"),
                   NextValue(transfer_done_rio_phy, 1))
                )
        self.submodules.fsm_rio_phy = fsm_rio_phy

        self.sync.rio_phy += [
            trigger_rio_phy.eq(0),
            If(self.rtlink.o.stb,
               If(self.rtlink.o.address == 0, trigger_rio_phy.eq(1)),
               If(self.rtlink.o.address == 1, Cat(pretrigger_len_rio_phy, posttrigger_len_rio_phy).eq(self.rtlink.o.data[0:24]))
            )
        ]

        self.comb += [
            self.rtlink.i.data.eq(memory_read_port.dat_r)
        ]

        # --------------------------------------------------------------------------------------------------------------
        # CDC dclk -> rio_phy

        self.comb += [data_start_address_reg_rio_phy.eq(data_start_address_reg_dclk)]
        cdc_transfer_en_dclk_rio_phy = PulseSynchronizer(idomain="dclk", odomain="rio_phy")
        self.submodules.cdc_transfer_en_dclk_rio_phy = cdc_transfer_en_dclk_rio_phy
        self.comb += [
            cdc_transfer_en_dclk_rio_phy.i.eq(transfer_en_dclk),
            transfer_en_rio_phy.eq(cdc_transfer_en_dclk_rio_phy.o)
        ]

        # --------------------------------------------------------------------------------------------------------------
        # CDC rio_phy -> dclk

        cdc_rio_phy_dclk = BusSynchronizer(24, idomain="rio_phy", odomain="dclk")
        self.submodules.cdc_rio_phy_dclk = cdc_rio_phy_dclk
        self.comb += [
            cdc_rio_phy_dclk.i.eq(Cat(pretrigger_len_rio_phy, posttrigger_len_rio_phy)),
            Cat(pretrigger_len_dclk, posttrigger_len_dclk).eq(cdc_rio_phy_dclk.o)
        ]
        cdc_trigger_rio_phy_dclk = PulseSynchronizer(idomain="rio_phy", odomain="dclk")
        self.submodules.cdc_trigger_rio_phy_dclk = cdc_trigger_rio_phy_dclk
        self.comb += [
            cdc_trigger_rio_phy_dclk.i.eq(trigger_rio_phy),
            trigger_dclk.eq(cdc_trigger_rio_phy_dclk.o)
        ]
        cdc_transfer_done_rio_phy_dclk = PulseSynchronizer(idomain="rio_phy", odomain="dclk")
        self.submodules.cdc_transfer_done_rio_phy_dclk = cdc_transfer_done_rio_phy_dclk
        self.comb += [
            cdc_transfer_done_rio_phy_dclk.i.eq(transfer_done_rio_phy),
            transfer_done_dclk.eq(cdc_transfer_done_rio_phy_dclk.o)
        ]


class SimulationWrapper(Module):

    def __init__(self):

        self.data_clk = Signal()
        self.data = Signal(10)

        self.clock_domains.cd_rio_phy = cd_rio_phy = ClockDomain()
        self.clock_domains.cd_dclk = cd_dclk = ClockDomain()

        self.comb += [cd_dclk.clk.eq(self.data_clk)]

        self.submodules.dut = dut = AdcPhyDaq(self.data_clk, self.data, 2048)

        self.io = {
            cd_dclk.rst,
            self.data_clk,
            self.data,
            cd_rio_phy.clk,
            cd_rio_phy.rst,
            dut.rtlink.i.stb,
            dut.rtlink.i.data,
            dut.rtlink.o.stb,
            dut.rtlink.o.address,
            dut.rtlink.o.data
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
                    create_clock_domains=False).write("adc_phy_daq.v")
    update_tb("adc_phy_daq.v")