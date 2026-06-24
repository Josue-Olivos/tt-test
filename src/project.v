/*
 * Copyright (c) 2024 Josue Olivos
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

/*
 * Tiny Tapeout top-level module for a 4-bit ALU.
 * This module follows the required Tiny Tapeout pin interface:
 * This ALU is combinational, so it does not actually use clk or rst_n.
 * The outputs update whenever the inputs or opcode change.
 */

module tt_um_josue_olivos_alu (
    input  wire [7:0] ui_in,    // 8 Dedicated input pins from Tiny Tapeout
    output wire [7:0] uo_out,   // 8 Dedicated output pins to Tiny Tapeout
    input  wire [7:0] uio_in,   // 8 Bidirectional pins read as inputs
    output wire [7:0] uio_out,  // 8 Bidirectional pins driven as outputs
    output wire [7:0] uio_oe,   // 8 Output-enable for bidirectional pins
    input  wire       ena,      // Enable signal, normally high when powered
    input  wire       clk,      // Clock signal, unused in this combinational ALU
    input  wire       rst_n     // Active-low reset, unused in this combinational ALU
);

  /*
   * Internal signal mapping
   * The 8 dedicated input pins are split into two 4-bit operands:
   */

  // Connect Tiny Tapeout input pins to internal ALU operands.
  wire [3:0] a;             // First 4-bit ALU operand
  wire [3:0] b;             // Second 4-bit ALU operand 
  assign a = ui_in[3:0];    // ui_in[3:0] = operand A
  assign b = ui_in[7:4];    // ui_in[7:4] = operand B

  reg  [3:0] result;  // 4-bit output of the selected operation
  reg  carry_out;     // carry flag for addition, or borrow-related flag for subtraction
  
  wire [2:0] opcode;              // Operation selector
  assign opcode = uio_in[2:0];    // Use only the lower 3 bits of uio_in as the operation selector.

  wire zero_flag;     // Goes high when result equals exactly 0000
  assign zero_flag = (result == 4'b0000);

  /*
   * Combinational ALU logic
   * always @(*) means this block re-evaluates whenever any signal used inside
   * the block changes. This is what we want for combinational logic.
   * The default assignments at the top prevent unwanted latch inference.
   * Every time the block runs, result and carry_out start with known values.
   */
    
  always @(*) begin
    result = 4'b0000;
    carry_out = 1'b0;

    case (opcode)

      // Addition: add A and B.
      // The result is 4 bits, and the 5th bit becomes carry_out.
      3'b000: begin
        {carry_out, result} = a + b;
      end

      // Subtraction: subtract B from A.
      // Since result is 4 bits, negative values wrap around in two's-complement style.
      // The extra bit is stored in carry_out.
      3'b001: begin
        {carry_out, result} = a - b;
      end

      // Bitwise AND.
      // Each bit of A is ANDed with the matching bit of B.
      3'b010: begin
        result = a & b;
      end

      // Bitwise OR.
      // Each bit of A is ORed with the matching bit of B.
      3'b011: begin
        result = a | b;
      end

      // Bitwise XOR.
      // Each result bit is 1 only when the matching A and B bits are different.
      3'b100: begin
        result = a ^ b;
      end

      // Bitwise NOT of A.
      // B is ignored for this operation.
      3'b101: begin
        result = ~a;
      end

      // Logical shift left by 1.
      // Example: 0111 becomes 1110.
      // The leftmost bit is discarded and a 0 enters on the right.
      3'b110: begin
        result = a << 1;
      end

      // Logical shift right by 1.
      // Example: 1000 becomes 0100.
      // The rightmost bit is discarded and a 0 enters on the left.
      3'b111: begin
        result = a >> 1;
      end

      // Default safety case.
      // This should not happen because opcode is 3 bits and all 8 cases are covered,
      // but it is good practice to include a default.
      default: begin
        result = 4'b0000;
        carry_out = 1'b0;
      end

    endcase
  end

  /*
   * Output mapping
   * The 8 dedicated output pins are assigned as:
   */

assign uo_out[3:0] = result;    //4-bit ALU result
assign uo_out[4]   = carry_out;    //carry_out flag
assign uo_out[5]   = zero_flag;    //zero_flag
assign uo_out[6]   = 1'b0;    //unused, tied to 0
assign uo_out[7]   = 1'b0;    //unused, tied to 0

  /*
   * Bidirectional pin handling
   * This project only uses the bidirectional pins as inputs through uio_in.
   * It does not drive any bidirectional outputs.
   * Therefore:
   *   uio_out = 0
   *   uio_oe  = 0
   * uio_oe controls whether each bidirectional pin is an output.
   * A value of 0 means input mode.
   */

  assign uio_out = 8'b0000_0000;
  assign uio_oe  = 8'b0000_0000;

  /*
   * Unused signal handling
   *
   * Tiny Tapeout designs should avoid leaving inputs completely unused,
   * because synthesis/lint tools may generate warnings.
   *
   * This line safely "uses" the unused inputs without affecting the design.
   *
   * In this ALU:
   *   ena is unused
   *   clk is unused
   *   rst_n is unused
   *   uio_in[7:3] are unused
   *
   * The final 1'b0 prevents this reduction-AND expression from ever being
   * optimized into meaningful logic.
   */

  wire _unused = &{ena, clk, rst_n, uio_in[7:3], 1'b0};

endmodule
