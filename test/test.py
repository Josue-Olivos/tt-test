# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import Timer


# Helper function to set the ALU inputs.
# ui_in holds both 4-bit inputs:
#   lower 4 bits = a
#   upper 4 bits = b
# uio_in holds the opcode that selects the ALU operation.
def set_alu_inputs(dut, a, b, opcode):
    dut.ui_in.value = ((b & 0xF) << 4) | (a & 0xF)
    dut.uio_in.value = opcode


# Read the lower 4 bits of uo_out as the ALU result.
def result(dut):
    return int(dut.uo_out.value) & 0xF


# Read bit 4 of uo_out as the carry flag.
def carry(dut):
    return (int(dut.uo_out.value) >> 4) & 1


# Read bit 5 of uo_out as the zero flag.
def zero(dut):
    return (int(dut.uo_out.value) >> 5) & 1


@cocotb.test()
async def test_project(dut):

    dut._log.info("Starting ALU tests")

    # Enable the Tiny Tapeout design and keep it out of reset.
    dut.ena.value = 1
    dut.rst_n.value = 1

    #
    # ADD: 5 + 3 = 8
    #
    set_alu_inputs(dut, 5, 3, 0b000)
    await Timer(1, unit="ns")

    assert result(dut) == 8
    assert carry(dut) == 0
    assert zero(dut) == 0

    #
    # ADD WITH CARRY: 15 + 1 = 16
    # The 4-bit result wraps to 0, and the carry flag becomes 1.
    #
    set_alu_inputs(dut, 15, 1, 0b000)
    await Timer(1, unit="ns")

    assert result(dut) == 0
    assert carry(dut) == 1
    assert zero(dut) == 1

    #
    # SUBTRACT: 8 - 3 = 5
    #
    set_alu_inputs(dut, 8, 3, 0b001)
    await Timer(1, unit="ns")

    assert result(dut) == 5

    #
    # AND: 1100 & 1010 = 1000
    #
    set_alu_inputs(dut, 12, 10, 0b010)
    await Timer(1, unit="ns")

    assert result(dut) == 8

    #
    # OR: 1100 | 1010 = 1110
    #
    set_alu_inputs(dut, 12, 10, 0b011)
    await Timer(1, unit="ns")

    assert result(dut) == 14

    #
    # XOR: 1111 ^ 0101 = 1010
    #
    set_alu_inputs(dut, 15, 5, 0b100)
    await Timer(1, unit="ns")

    assert result(dut) == 10

    #
    # NOT: ~1010 = 0101
    # Only input a is used for this operation.
    #
    set_alu_inputs(dut, 10, 0, 0b101)
    await Timer(1, unit="ns")

    assert result(dut) == 5

    #
    # SHIFT LEFT: 0111 << 1 = 1110
    #
    set_alu_inputs(dut, 7, 0, 0b110)
    await Timer(1, unit="ns")

    assert result(dut) == 14

    #
    # SHIFT RIGHT: 1000 >> 1 = 0100
    #
    set_alu_inputs(dut, 8, 0, 0b111)
    await Timer(10, unit="ns")

    assert result(dut) == 4

    dut._log.info("ALL ALU TESTS PASSED")
