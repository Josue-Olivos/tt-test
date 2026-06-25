# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import Timer


def set_alu_inputs(dut, a, b, opcode):
    dut.ui_in.value = ((b & 0xF) << 4) | (a & 0xF)
    dut.uio_in.value = opcode


def result(dut):
    return int(dut.uo_out.value) & 0xF


def carry(dut):
    return (int(dut.uo_out.value) >> 4) & 1


def zero(dut):
    return (int(dut.uo_out.value) >> 5) & 1


@cocotb.test()
async def test_project(dut):

    dut._log.info("Starting ALU tests")

    dut.ena.value = 1
    dut.rst_n.value = 1

    #
    # ADD
    #
    set_alu_inputs(dut, 5, 3, 0b000)
    await Timer(1, unit="ns")

    assert result(dut) == 8
    assert carry(dut) == 0
    assert zero(dut) == 0

    #
    # ADD WITH CARRY
    #
    set_alu_inputs(dut, 15, 1, 0b000)
    await Timer(1, unit="ns")

    assert result(dut) == 0
    assert carry(dut) == 1
    assert zero(dut) == 1

    #
    # SUBTRACT
    #
    set_alu_inputs(dut, 8, 3, 0b001)
    await Timer(1, unit="ns")

    assert result(dut) == 5

    #
    # AND
    #
    set_alu_inputs(dut, 12, 10, 0b010)
    await Timer(1, unit="ns")

    assert result(dut) == 8

    #
    # OR
    #
    set_alu_inputs(dut, 12, 10, 0b011)
    await Timer(1, unit="ns")

    assert result(dut) == 14

    #
    # XOR
    #
    set_alu_inputs(dut, 15, 5, 0b100)
    await Timer(1, unit="ns")

    assert result(dut) == 10

    #
    # NOT
    #
    set_alu_inputs(dut, 10, 0, 0b101)
    await Timer(1, unit="ns")

    assert result(dut) == 5

    #
    # SHIFT LEFT
    #
    set_alu_inputs(dut, 7, 0, 0b110)
    await Timer(1, unit="ns")

    assert result(dut) == 14

    #
    # SHIFT RIGHT
    #
    set_alu_inputs(dut, 8, 0, 0b111)
    await Timer(10, unit="ns")

    assert result(dut) == 4

    dut._log.info("ALL ALU TESTS PASSED")
