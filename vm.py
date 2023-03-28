from dataclasses import dataclass, field
from typing import TextIO
import sys


@dataclass
class Instruction:
    vm: "VirtualMachine" = field(repr=False)
    index: int

    def _execute(self):
        pass

    def execute(self) -> int:
        self._execute()
        return self.index + 1


class Increment(Instruction):
    def _execute(self):
        self.vm.memory[self.vm.pointer] += 1


class Decrement(Instruction):
    def _execute(self):
        self.vm.memory[self.vm.pointer] -= 1


class MoveRight(Instruction):
    def _execute(self):
        self.vm.pointer += 1


class MoveLeft(Instruction):
    def _execute(self):
        self.vm.pointer -= 1


class Read(Instruction):
    def _execute(self):
        self.vm.memory[self.vm.pointer] = ord(self.vm.stdin.read(1))


class Write(Instruction):
    def _execute(self):
        self.vm.stdout.write(chr(self.vm.memory[self.vm.pointer]))


@dataclass
class LoopEnd(Instruction):
    jump_to: int

    def _execute(self):
        if self.vm.memory[self.vm.pointer] == 0:
            return self.index + 1
        return self.jump_to

    def execute(self) -> int:
        return self._execute()


@dataclass
class LoopStart(Instruction):
    jump_to: int

    def _execute(self):
        if self.vm.memory[self.vm.pointer] != 0:
            return self.index + 1
        return self.jump_to

    def execute(self) -> int:
        return self._execute()


INSTRUCTION_MAPPING = {
    ">": MoveRight,
    "<": MoveLeft,
    "+": Increment,
    "-": Decrement,
    ".": Write,
    ",": Read,
    "[": LoopStart,
    "]": LoopEnd,
}


@dataclass
class VirtualMachine:
    memory: bytearray = field(default_factory=lambda: bytearray(30000), repr=False)
    instructions: list[Instruction] = field(default_factory=list)
    pointer: int = 0
    stdin: TextIO = sys.stdin
    stdout: TextIO = sys.stdout

    def reset(self):
        self.memory = [0] * 30000
        self.pointer = 0

    def clear(self):
        self.reset()
        self.instructions = []

    def compile(self, code: str):
        self.clear()
        index = 0
        left = -1
        for ch in code:
            instruction = INSTRUCTION_MAPPING.get(ch)
            match instruction:
                case None:
                    pass
                case x if x == LoopStart:
                    left = index
                    self.instructions.append(LoopStart(self, index, -1))
                case x if x == LoopEnd:
                    assert left != -1, "Unmatched ]"
                    setattr(self.instructions[left], "jump_to", index)
                    self.instructions.append(LoopEnd(self, index, jump_to=left))
                    left = -1
                case _:
                    self.instructions.append(instruction(self, index))
            index += bool(instruction)
        assert left == -1, "Unmatched ["

    def run(self):
        index = 0
        cnt = len(self.instructions)
        while (index := self.instructions[index].execute()) < cnt:
            pass
