import cocotb

from cocotb.triggers import Timer, RisingEdge, FallingEdge, Combine, Edge, Event
from cocotb.clock import Clock
from cocotb.result import TestSuccess, TestError
from random import randint
from itertools import product


def int_to_bits(i, length):
    if i < 0:
        raise ValueError("Number mus be >= 0")
    return [int(x) for x in bin(i)[2:].zfill(length)]

# noinspection PyStatementEffect
class TbTdcGpx2Daq:

    def __init__(self, dut):
        self.dut = dut

        cocotb.fork(Clock(self.dut.rio_phy_clk, 8000).start())
        cocotb.fork(Clock(self.dut.dclk_clk, 10000).start())

        self.rtio_re = RisingEdge(self.dut.rio_phy_clk)
        self.rtio_fe = FallingEdge(self.dut.rio_phy_clk)
        self.dclk_re = RisingEdge(self.dut.dclk_clk)
        self.dclk_fe = FallingEdge(self.dut.dclk_clk)

        self.rtlink = {
            "main": {
                "clock": self.dut.rio_phy_clk,
                "input": {
                    "stb": dut.rtlink_stb_o,
                    "data": dut.rtlink_data_o},
                 "output": {
                     "stb": dut.rtlink_stb_i,
                     "data": dut.rtlink_data_i,
                     "addr": dut.rtlink_adr_i}
            }
        }

        self.collected_data = []  # From rlink
        self.monitor_data = []
        self.monitor_trigger = []

    @cocotb.coroutine
    def write_rtlink(self, channel, address, data):
        self.dut._log.info(f"Writing to rtlink {channel} address {address}")

        link_clock = self.rtlink[channel]["clock"]
        link_addr = self.rtlink[channel]["output"].get("addr", None)
        link_data = self.rtlink[channel]["output"]["data"]
        link_stb  = self.rtlink[channel]["output"]["stb"]

        yield FallingEdge(link_clock)

        if link_addr:
            link_addr <= address
        if link_data:
            link_data <= data

        link_stb <= 0x1
        yield FallingEdge(link_clock)
        link_stb <= 0x0

    @cocotb.coroutine
    def rtlink_collector(self, channel, callback):
        link_clock = self.rtlink[channel]["clock"]

        link_data = self.rtlink[channel]["input"]["data"]
        link_stb = self.rtlink[channel]["input"]["stb"]

        while True:
            yield RisingEdge(link_clock)
            if link_stb == 1:
                callback(link_data.value.binstr)

    def data_sink(self, target):
        def data_sink_wrapped(data):
            target.append(int(data, 2))
        return data_sink_wrapped

    @cocotb.coroutine
    def reset(self):
        self.dut.data_i <= 0
        self.dut.data_stb_i <= 0
        self.dut.dclk_rst <= 0
        self.dut.rio_phy_rst <= 0
        self.dut.trigger <= 0

        self.dut._log.info("Waiting initial 120 ns")
        yield Timer(120, 'ns')
        self.dut._log.info("Starting reset... ")
        self.dut.dclk_rst <= 1
        self.dut.rio_phy_rst <= 1
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        yield Combine(self.dclk_re, self.rtio_re)
        self.dut.dclk_rst <= 0
        self.dut.rio_phy_rst <= 0
        self.dut._log.info("Reset finished")

    @cocotb.coroutine
    def data_trigger_monitor(self):
        dclk_num = 0
        trig_num = 0
        while True:
            yield self.dclk_re
            if self.dut.data_stb_i == 1:
                self.monitor_data.append((dclk_num, int(self.dut.data_i.value.binstr, 2)))
            if self.dut.trigger == 1:
                self.monitor_trigger.append((dclk_num, trig_num))
                trig_num += 1
            dclk_num += 1

    @cocotb.coroutine
    def data_generator(self):
        val = 0
        while True:
            yield self.dclk_fe
            self.dut.data_i <= val
            self.dut.data_stb_i <= 0
            if val % 10 == 0:
                self.dut.data_stb_i <= 1
            val = val+1 #if val < 4096 else 0

    @cocotb.coroutine
    def simple_run(self, pretrigger, posttrigger):
        dgen = cocotb.fork(self.data_generator())
        dmon = cocotb.fork(self.data_trigger_monitor())
        
        yield self.reset()
        yield Timer(100, 'ns')
        collector = cocotb.fork(self.rtlink_collector("main", self.data_sink(self.collected_data)))
        yield self.write_rtlink("main", 0, pretrigger)
        yield self.write_rtlink("main", 1, posttrigger)
        
        yield Timer(50, 'ns')
        
        yield Timer(50, 'us')
        yield self.dclk_fe
        self.dut.trigger <= 1
        yield self.dclk_fe
        self.dut.trigger <= 0
        yield Timer(10, 'us')

        dgen.kill()
        dmon.kill()

        for trigger_idx, trigger_num in self.monitor_trigger:
            data_idx_min = trigger_idx-pretrigger
            data_idx_max = trigger_idx+posttrigger-1
            data_for_trigger = filter(lambda x: data_idx_min <= x[0] <= data_idx_max, self.monitor_data)        
            print(f"Trigger: {trigger_idx}/{trigger_num}:", [x[1] for x in list(data_for_trigger)])
        
        for x in self.collected_data:
            print("trigcnt: {} data: {}".format(x & 0xF, x >> 4))


@cocotb.test()
def test(dut):
    tb = TbTdcGpx2Daq(dut)
    yield tb.simple_run(20, 20)

    # for s in [0, 1, 100]:
    #     yield tb.run_for_separation(s, 5, 5)
