from migen import *
from migen.genlib.cdc import MultiReg, BusSynchronizer


class XilinxProbeAsync(Module):
    def __init__(self, signal, name=None, odomain="sys", idomain=None, **kwargs):
        probe_signal = Signal.like(signal)
        probe_signal.attr.add(("mark_debug", "true"))
        if name:
            probe_signal.name_override = name
        if len(signal) > 1 and idomain is None:
            raise ValueError("idomain required for signal length > 1")            
        cdc = BusSynchronizer(width=len(signal), idomain=idomain, odomain=odomain)
        cd = getattr(self.sync, odomain)
        cd += (probe_signal.eq(cdc.o))
        self.comb += [cdc.i.eq(signal)]
        self.submodules += cdc
        

class XilinxProbe(Module):
    def __init__(self, signal, name=None):
        signal.attr.add(("mark_debug", "true"))
        if name:
            signal.name_override = name