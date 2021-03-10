/* Machine-generated using Migen */

`timescale 1ns/1ps

module top(
	input [21:0] data_i,
	input data_stb_i,
	input trigger,
	input rio_phy_clk,
	input rio_phy_rst,
	output dclk_clk,
	input dclk_rst,
	input rtlink_stb_i,
	input [6:0] rtlink_data_i,
	input [1:0] rtlink_adr_i,
	output rtlink_stb_o,
	output [25:0] rtlink_data_o
);

reg dclk_clk_1 = 1'd0;
reg [6:0] pretrigger_rio_phy = 7'd0;
reg [6:0] posttrigger_rio_phy = 7'd0;
wire [6:0] pretrigger_dclk;
wire [6:0] posttrigger_dclk;
wire trigger_dclk;
reg [3:0] trigger_cnt = 4'd0;
reg trigger_d = 1'd0;
wire [22:0] cb_data_in;
wire [22:0] data_in;
wire we;
wire [6:0] pretrigger;
wire [6:0] posttrigger;
wire trigger1;
wire [22:0] data_out;
reg stb_out = 1'd0;
wire [6:0] wr_port_adr;
wire [22:0] wr_port_dat_r;
wire wr_port_we;
wire [22:0] wr_port_dat_w;
wire [6:0] rd_port_adr;
wire [22:0] rd_port_dat_r;
reg rd_port_re = 1'd0;
reg [6:0] wr_ptr = 7'd0;
reg [6:0] rd_ptr = 7'd0;
reg [6:0] readout_cnt = 7'd0;
wire re;
reg readable = 1'd0;
reg [22:0] dout = 23'd0;
wire asyncfifo_we;
wire asyncfifo_writable;
wire asyncfifo_re;
wire asyncfifo_readable;
wire [22:0] asyncfifo_din;
wire [22:0] asyncfifo_dout;
wire graycounter0_ce;
(* no_retiming = "true" *) reg [4:0] graycounter0_q = 5'd0;
wire [4:0] graycounter0_q_next;
reg [4:0] graycounter0_q_binary = 5'd0;
reg [4:0] graycounter0_q_next_binary;
wire graycounter1_ce;
(* no_retiming = "true" *) reg [4:0] graycounter1_q = 5'd0;
wire [4:0] graycounter1_q_next;
reg [4:0] graycounter1_q_binary = 5'd0;
reg [4:0] graycounter1_q_next_binary;
wire [4:0] produce_rdomain;
wire [4:0] consume_wdomain;
wire [3:0] wrport_adr;
wire [22:0] wrport_dat_r;
wire wrport_we;
wire [22:0] wrport_dat_w;
wire [3:0] rdport_adr;
wire [22:0] rdport_dat_r;
wire i;
wire o;
reg toggle_i = 1'd0;
wire toggle_o;
reg toggle_o_r = 1'd0;
reg state = 1'd0;
reg next_state;
reg rd_port_re_next_value0;
reg rd_port_re_next_value_ce0;
reg [6:0] readout_cnt_next_value1;
reg readout_cnt_next_value_ce1;
reg stb_out_next_value2;
reg stb_out_next_value_ce2;
(* async_reg = "true", mr_ff = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [4:0] xilinxmultiregimpl0_regs0 = 5'd0;
(* async_reg = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [4:0] xilinxmultiregimpl0_regs1 = 5'd0;
(* async_reg = "true", mr_ff = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [4:0] xilinxmultiregimpl1_regs0 = 5'd0;
(* async_reg = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [4:0] xilinxmultiregimpl1_regs1 = 5'd0;
(* async_reg = "true", mr_ff = "true", no_retiming = "true", no_shreg_extract = "true" *) reg xilinxmultiregimpl2_regs0 = 1'd0;
(* async_reg = "true", no_retiming = "true", no_shreg_extract = "true" *) reg xilinxmultiregimpl2_regs1 = 1'd0;
(* async_reg = "true", mr_ff = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [6:0] xilinxmultiregimpl3_regs0 = 7'd0;
(* async_reg = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [6:0] xilinxmultiregimpl3_regs1 = 7'd0;
(* async_reg = "true", mr_ff = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [6:0] xilinxmultiregimpl4_regs0 = 7'd0;
(* async_reg = "true", no_retiming = "true", no_shreg_extract = "true" *) reg [6:0] xilinxmultiregimpl4_regs1 = 7'd0;

// synthesis translate_off
reg dummy_s;
initial dummy_s <= 1'd0;
// synthesis translate_on

assign dclk_clk = dclk_clk_1;
assign cb_data_in = {data_i, trigger_cnt, data_stb_i};
assign i = trigger;
assign trigger_dclk = o;
assign data_in = cb_data_in;
assign we = 1'd1;
assign trigger1 = trigger_dclk;
assign pretrigger = pretrigger_dclk;
assign posttrigger = posttrigger_dclk;
assign asyncfifo_din = data_out;
assign re = readable;
assign asyncfifo_we = stb_out;
assign rtlink_data_o = dout[22:1];
assign rtlink_stb_o = (dout[0] & readable);
assign wr_port_we = we;
assign wr_port_adr = wr_ptr;
assign wr_port_dat_w = data_in;
assign rd_port_adr = rd_ptr;
assign data_out = rd_port_dat_r;

// synthesis translate_off
reg dummy_d;
// synthesis translate_on
always @(*) begin
	next_state <= 1'd0;
	rd_port_re_next_value0 <= 1'd0;
	rd_port_re_next_value_ce0 <= 1'd0;
	readout_cnt_next_value1 <= 7'd0;
	readout_cnt_next_value_ce1 <= 1'd0;
	stb_out_next_value2 <= 1'd0;
	stb_out_next_value_ce2 <= 1'd0;
	next_state <= state;
	case (state)
		1'd1: begin
			if ((readout_cnt == 1'd0)) begin
				next_state <= 1'd0;
				rd_port_re_next_value0 <= 1'd0;
				rd_port_re_next_value_ce0 <= 1'd1;
				stb_out_next_value2 <= 1'd0;
				stb_out_next_value_ce2 <= 1'd1;
			end else begin
				readout_cnt_next_value1 <= (readout_cnt - 1'd1);
				readout_cnt_next_value_ce1 <= 1'd1;
				rd_port_re_next_value0 <= 1'd1;
				rd_port_re_next_value_ce0 <= 1'd1;
				stb_out_next_value2 <= 1'd1;
				stb_out_next_value_ce2 <= 1'd1;
			end
		end
		default: begin
			if ((trigger1 == 1'd1)) begin
				next_state <= 1'd1;
				rd_port_re_next_value0 <= 1'd1;
				rd_port_re_next_value_ce0 <= 1'd1;
				readout_cnt_next_value1 <= (pretrigger + posttrigger);
				readout_cnt_next_value_ce1 <= 1'd1;
			end else begin
				rd_port_re_next_value0 <= 1'd0;
				rd_port_re_next_value_ce0 <= 1'd1;
			end
		end
	endcase
// synthesis translate_off
	dummy_d <= dummy_s;
// synthesis translate_on
end
assign asyncfifo_re = (re | (~readable));
assign graycounter0_ce = (asyncfifo_writable & asyncfifo_we);
assign graycounter1_ce = (asyncfifo_readable & asyncfifo_re);
assign asyncfifo_writable = (((graycounter0_q[4] == consume_wdomain[4]) | (graycounter0_q[3] == consume_wdomain[3])) | (graycounter0_q[2:0] != consume_wdomain[2:0]));
assign asyncfifo_readable = (graycounter1_q != produce_rdomain);
assign wrport_adr = graycounter0_q_binary[3:0];
assign wrport_dat_w = asyncfifo_din;
assign wrport_we = graycounter0_ce;
assign rdport_adr = graycounter1_q_next_binary[3:0];
assign asyncfifo_dout = rdport_dat_r;

// synthesis translate_off
reg dummy_d_1;
// synthesis translate_on
always @(*) begin
	graycounter0_q_next_binary <= 5'd0;
	if (graycounter0_ce) begin
		graycounter0_q_next_binary <= (graycounter0_q_binary + 1'd1);
	end else begin
		graycounter0_q_next_binary <= graycounter0_q_binary;
	end
// synthesis translate_off
	dummy_d_1 <= dummy_s;
// synthesis translate_on
end
assign graycounter0_q_next = (graycounter0_q_next_binary ^ graycounter0_q_next_binary[4:1]);

// synthesis translate_off
reg dummy_d_2;
// synthesis translate_on
always @(*) begin
	graycounter1_q_next_binary <= 5'd0;
	if (graycounter1_ce) begin
		graycounter1_q_next_binary <= (graycounter1_q_binary + 1'd1);
	end else begin
		graycounter1_q_next_binary <= graycounter1_q_binary;
	end
// synthesis translate_off
	dummy_d_2 <= dummy_s;
// synthesis translate_on
end
assign graycounter1_q_next = (graycounter1_q_next_binary ^ graycounter1_q_next_binary[4:1]);
assign o = (toggle_o ^ toggle_o_r);
assign produce_rdomain = xilinxmultiregimpl0_regs1;
assign consume_wdomain = xilinxmultiregimpl1_regs1;
assign toggle_o = xilinxmultiregimpl2_regs1;
assign pretrigger_dclk = xilinxmultiregimpl3_regs1;
assign posttrigger_dclk = xilinxmultiregimpl4_regs1;

always @(posedge dclk_clk) begin
	if ((trigger_dclk & (~trigger_d))) begin
		trigger_cnt <= (trigger_cnt + 1'd1);
	end
	trigger_d <= trigger_dclk;
	if (we) begin
		rd_ptr <= ((wr_ptr - pretrigger) + 1'd1);
		wr_ptr <= (wr_ptr + 1'd1);
	end
	state <= next_state;
	if (rd_port_re_next_value_ce0) begin
		rd_port_re <= rd_port_re_next_value0;
	end
	if (readout_cnt_next_value_ce1) begin
		readout_cnt <= readout_cnt_next_value1;
	end
	if (stb_out_next_value_ce2) begin
		stb_out <= stb_out_next_value2;
	end
	graycounter0_q_binary <= graycounter0_q_next_binary;
	graycounter0_q <= graycounter0_q_next;
	toggle_o_r <= toggle_o;
	if (dclk_rst) begin
		trigger_cnt <= 4'd0;
		trigger_d <= 1'd0;
		stb_out <= 1'd0;
		rd_port_re <= 1'd0;
		wr_ptr <= 7'd0;
		rd_ptr <= 7'd0;
		readout_cnt <= 7'd0;
		graycounter0_q <= 5'd0;
		graycounter0_q_binary <= 5'd0;
		state <= 1'd0;
	end
	xilinxmultiregimpl1_regs0 <= graycounter1_q;
	xilinxmultiregimpl1_regs1 <= xilinxmultiregimpl1_regs0;
	xilinxmultiregimpl2_regs0 <= toggle_i;
	xilinxmultiregimpl2_regs1 <= xilinxmultiregimpl2_regs0;
	xilinxmultiregimpl3_regs0 <= pretrigger_rio_phy;
	xilinxmultiregimpl3_regs1 <= xilinxmultiregimpl3_regs0;
	xilinxmultiregimpl4_regs0 <= posttrigger_rio_phy;
	xilinxmultiregimpl4_regs1 <= xilinxmultiregimpl4_regs0;
end

always @(posedge rio_phy_clk) begin
	if (rtlink_stb_i) begin
		if ((rtlink_adr_i == 1'd0)) begin
			pretrigger_rio_phy <= rtlink_data_i;
		end
		if ((rtlink_adr_i == 1'd1)) begin
			posttrigger_rio_phy <= rtlink_data_i;
		end
	end
	if ((re | (~readable))) begin
		dout <= asyncfifo_dout;
		readable <= asyncfifo_readable;
	end
	graycounter1_q_binary <= graycounter1_q_next_binary;
	graycounter1_q <= graycounter1_q_next;
	if (i) begin
		toggle_i <= (~toggle_i);
	end
	if (rio_phy_rst) begin
		pretrigger_rio_phy <= 7'd0;
		posttrigger_rio_phy <= 7'd0;
		readable <= 1'd0;
		graycounter1_q <= 5'd0;
		graycounter1_q_binary <= 5'd0;
	end
	xilinxmultiregimpl0_regs0 <= graycounter0_q;
	xilinxmultiregimpl0_regs1 <= xilinxmultiregimpl0_regs0;
end

reg [22:0] buffer[0:127];
reg [6:0] memadr;
reg [6:0] memadr_1;
always @(posedge dclk_clk) begin
	if (wr_port_we)
		buffer[wr_port_adr] <= wr_port_dat_w;
	memadr <= wr_port_adr;
end

always @(posedge dclk_clk) begin
	if (rd_port_re)
		memadr_1 <= rd_port_adr;
end

assign wr_port_dat_r = buffer[memadr];
assign rd_port_dat_r = buffer[memadr_1];

reg [22:0] storage[0:15];
reg [3:0] memadr_2;
reg [3:0] memadr_3;
always @(posedge dclk_clk) begin
	if (wrport_we)
		storage[wrport_adr] <= wrport_dat_w;
	memadr_2 <= wrport_adr;
end

always @(posedge rio_phy_clk) begin
	memadr_3 <= rdport_adr;
end

assign wrport_dat_r = storage[memadr_2];
assign rdport_dat_r = storage[memadr_3];

`ifdef COCOTB_SIM
initial begin
  $dumpfile ("top.vcd");
  $dumpvars (0, top);
  #1;
end
`endif

endmodule

