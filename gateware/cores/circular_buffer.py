import random

from migen import *
from migen.genlib.fsm import FSM


class CircularBiffer(Module):
    
    def __init__(self, data_width=44, length=128):
        
        self.data_in = Signal(data_width)
        self.we = Signal()

        self.pretrigger = Signal(max=length-1)
        self.posttrigger = Signal(max=length-1)  
        self.trigger = Signal()

        self.data_out = Signal(data_width)
        self.stb_out = Signal()   

        # # #

        buffer = Memory(data_width, length)
        wr_port = buffer.get_port(write_capable=True)
        rd_port = buffer.get_port(has_re=True)
        self.specials += [buffer, wr_port, rd_port]
        
        wr_ptr = Signal.like(wr_port.adr)
        rd_ptr = Signal.like(rd_port.adr)

        self.comb += [
            wr_port.we.eq(self.we),
            wr_port.adr.eq(wr_ptr),
            wr_port.dat_w.eq(self.data_in),
            rd_port.adr.eq(rd_ptr),
            self.data_out.eq(rd_port.dat_r)
        ]
        self.sync += [
            If(self.we, 
                rd_ptr.eq(wr_ptr-self.pretrigger+1),
                wr_ptr.eq(wr_ptr+1),
                
            )
        ]

        readout_cnt = Signal(max=length-1)
        readout_fsm = FSM("IDLE")
        self.submodules += readout_fsm

        readout_fsm.act("IDLE",
            If(self.trigger == 1, 
                NextState("READOUT"),
                NextValue(rd_port.re, 1),
                NextValue(readout_cnt, self.pretrigger+self.posttrigger))
            .Else(
                NextValue(rd_port.re, 0)
            )
        )

        readout_fsm.act("READOUT",
            If(readout_cnt == 0, 
                NextState("IDLE"),
                NextValue(rd_port.re, 0),
                NextValue(self.stb_out, 0))
            .Else(
                NextValue(readout_cnt, readout_cnt-1),
                NextValue(rd_port.re, 1),
                NextValue(self.stb_out, 1),
            )
        )

def test_daq(dut, pretrigger=5, posttrigger=5):
    yield dut.we.eq(1)
    yield dut.pretrigger.eq(pretrigger)
    yield dut.posttrigger.eq(posttrigger)
    trigger_at = random.randint(64, 300)
    readout = []
    yield
    for t in range(512):
        yield dut.data_in.eq(t)
        yield dut.trigger.eq(0)
        if t == trigger_at:
            yield dut.trigger.eq(1)
        if (yield dut.stb_out):
            readout.append((yield dut.data_out))
        yield
    expected_readout = [trigger_at+i-pretrigger+1 for i in range(pretrigger+posttrigger)]
    print(f"{pretrigger} / {posttrigger}")
    print('='*40)
    print(expected_readout)
    print(readout)
    for i in range(len(expected_readout)):
        assert readout[i] == expected_readout[i]

def testbench(dut: CircularBiffer, pretrigger=5, posttrigger=5):
    for i in range(10):
        yield from test_daq(dut, 31, 32)
        yield from test_daq(dut, 1, 62)
        yield from test_daq(dut, 0, 63)
        yield from test_daq(dut, 63, 0)
        for j in range(10):
            pretrigger = random.randint(0, 63)
            posttrigger = 63-pretrigger
            yield from test_daq(dut, pretrigger, posttrigger)

if __name__ == "__main__":
    dut = CircularBiffer(44, 64)
    run_simulation(dut, testbench(dut), vcd_name="circular_buffer.vcd")
