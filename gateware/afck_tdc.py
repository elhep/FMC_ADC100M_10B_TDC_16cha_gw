import argparse

from migen import *
from artiq.build_soc import build_artiq_soc
from artiq.gateware.targets.afck1v1 import StandaloneBase, iostd_single, iostd_diff

from misoc.integration.builder import builder_args, builder_argdict
from misoc.cores import uart
from misoc.targets.afck1v1 import soc_afck1v1_argdict, soc_afck1v1_args

from gateware.cores.fmc_adc100M_10B_tdc_16cha import FmcAdc100M10b16chaTdc

from gateware.debug import XilinxProbeAsync, XilinxProbe
from gateware.cores.dac_spi import DacSpi


class AfckTdc(StandaloneBase):

    def add_design(self):
        FmcAdc100M10b16chaTdc.add_std(self, 1, iostd_single, iostd_diff, with_trig=True)
        #FmcAdc100M10b16chaTdc.add_std(self, 2, iostd_single, iostd_diff, with_trig=False)

        sclk = self.platform.request("vcxo_dac_sclk") 
        mosi = self.platform.request("vcxo_dac_din") 
        syncn = [
            self.platform.request("vcxo_dac1_sync_n"),
            self.platform.request("vcxo_dac2_sync_n")
        ]
        ncs = Signal()

        phy = DacSpi(sclk, mosi, ncs)
        self.submodules += phy
        self.comb += [s.eq(ncs) for s in syncn]

        # self.submodules += [
        #     XilinxProbe(self.uart_phy.tx.sink.data, "uart_tx_data"),
        #     XilinxProbe(self.uart_phy.tx.sink.stb, "uart_tx_stb"),
            
        #     XilinxProbe(self.ethmac.core.sink.stb, "ethmac_sink_stb"),
        #     XilinxProbe(self.ethmac.core.sink.data, "ethmac_sink_data"),
        #     XilinxProbe(self.ethmac.core.source.data, "ethmac_source_data"),
        #     XilinxProbe(self.ethmac.core.source.stb, "ethmac_source_stb"),
            
        #     XilinxProbe(self.ethphy.source.stb, "ethphy_source_stb"),
        #     XilinxProbe(self.ethphy.source.data, "ethphy_source_data"),
        #     XilinxProbe(self.ethphy.sink.stb, "ethphy_sink_stb"),
        #     XilinxProbe(self.ethphy.sink.data, "ethphy_sink_data"),
            
        #     XilinxProbe(self.ethmac.core.preamble_errors.status, "ethmac_preamble_errors"),
        #     XilinxProbe(self.ethmac.core.crc_errors.status, "ethmac_crc_errors"),

        # ]
       
        # self.platform.toolchain.postsynthesis_commands.append("source /workspace/gateware/debug/insert_ila.tcl")
        # self.platform.toolchain.postsynthesis_commands.append(
        #     "batch_insert_ila {1024}")
        # self.crg.cd_sys.clk.attr.add(("mark_dbg_hub_clk", "true"))
        # self.crg.cd_sys.clk.attr.add(("keep", "true"))
        # self.platform.toolchain.postsynthesis_commands.append(
        #     "connect_debug_port dbg_hub/clk [get_nets -hierarchical -filter {mark_dbg_hub_clk == true}]")


def main():
    parser = argparse.ArgumentParser(
        description="ARTIQ device binary builder for AFCK 1v1 systems")
    builder_args(parser)
    soc_afck1v1_args(parser)
    parser.set_defaults(output_dir="artiq_afck1v1")
    args = parser.parse_args()

    soc = AfckTdc(**soc_afck1v1_argdict(args))
    build_artiq_soc(soc, builder_argdict(args))


if __name__ == "__main__":
    main()

