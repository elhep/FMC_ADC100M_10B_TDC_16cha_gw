import argparse

from migen import *
from artiq.build_soc import build_artiq_soc
from artiq.gateware.targets.afck1v1 import StandaloneBase, iostd_single, iostd_diff
from gateware.cores.fmc_adc100M_10B_tdc_16cha import FmcAdc100M10b16chaTdc
from misoc.integration.builder import builder_args, builder_argdict
from misoc.targets.afck1v1 import soc_afck1v1_argdict, soc_afck1v1_args


class AfckTdc(StandaloneBase):

    def add_design(self):
        FmcAdc100M10b16chaTdc.add_std(self, 1, iostd_single, iostd_diff, with_trig=True)
        #FmcAdc100M10b16chaTdc.add_std(self, 2, iostd_single, iostd_diff, with_trig=False)

        # self.platform.toolchain.postsynthesis_commands.append("source /home/ms/data/pw/tdc/repo/gateware/debug/insert_ila.tcl")
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

