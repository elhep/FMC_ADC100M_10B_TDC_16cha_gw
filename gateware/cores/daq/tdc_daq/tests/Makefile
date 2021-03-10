VERILOG_SOURCES = $(XILINX_VIVADO)/data/verilog/src/glbl.v $(PWD)/../tdc_gpx2_daq.v
TOPLEVEL=top
MODULE=tb_tdc_gpx2_daq

COMPILE_ARGS=-y$(XILINX_VIVADO)/data/verilog/src/unisims -s glbl

include $(shell cocotb-config --makefiles)/Makefile.inc
include $(shell cocotb-config --makefiles)/Makefile.sim
