from dataclasses import dataclass, field
from typing import TextIO, Type
import sys
import os

MEMORY_SIZE = int(os.getenv("MEMORY_SIZE", 30000))


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
        self.vm.pointer = (self.vm.pointer + 1) % MEMORY_SIZE


class MoveLeft(Instruction):
    def _execute(self):
        self.vm.pointer = (self.vm.pointer - 1) % MEMORY_SIZE


class Read(Instruction):
    def _execute(self):
        self.vm.memory[self.vm.pointer] = ord(self.vm.input.read(1))


class Write(Instruction):
    def _execute(self):
        self.vm.output.write(chr(self.vm.memory[self.vm.pointer]))


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
    jump_to: int | None

    def _execute(self):
        if self.vm.memory[self.vm.pointer] != 0:
            return self.index + 1
        return self.jump_to

    def execute(self) -> int:
        return self._execute()


INSTRUCTION_MAPPING: dict[str, Type[Instruction]] = {
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
    memory: bytearray = field(
        default_factory=lambda: bytearray(MEMORY_SIZE), repr=False
    )
    instructions: list[Instruction] = field(default_factory=list)
    pointer: int = 0
    input: TextIO = field(default=sys.stdin, repr=False)
    output: TextIO = field(default=sys.stdout, repr=False)

    def reset(self):
        self.memory = [0] * MEMORY_SIZE
        self.pointer = 0

    def clear(self):
        self.reset()
        self.instructions = []

    def compile(self, code: str):
        self.clear()
        index = 0
        left: int | None = None
        for ch in code:
            instruction = INSTRUCTION_MAPPING.get(ch)
            if instruction:
                match instruction.__qualname__:
                    case "LoopStart":
                        left = index
                        self.instructions.append(LoopStart(self, index, None))
                    case "LoopEnd":
                        assert left is not None, "Unmatched ]"
                        setattr(self.instructions[left], "jump_to", index)
                        self.instructions.append(LoopEnd(self, index, jump_to=left))
                        left = None
                    case _:
                        self.instructions.append(instruction(self, index))
                index += bool(instruction)
        assert left == None, "Unmatched ["

    def run(self):
        index = 0
        cnt = len(self.instructions)
        while (index := self.instructions[index].execute()) < cnt:
            pass


def execute(code: str, input: TextIO = sys.stdin, output: TextIO = sys.stdout):
    vm = VirtualMachine(input=input, output=output)
    vm.compile(code)
    vm.run()
