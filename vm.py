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
    jump_to:int
    def _execute(self):
        if self.vm.memory[self.vm.pointer] == 0:
            return self.index + 1
        return self.jump_to

    def execute(self) -> int:
        return self._execute()

@dataclass
class LoopStart(Instruction):
    jump_to:int
    def _execute(self):
        if self.vm.memory[self.vm.pointer] != 0:
            return self.index + 1
        return self.jump_to

    def execute(self) -> int:
        return self._execute()


@dataclass
class VirtualMachine:
    memory: list[int] = field(default_factory=lambda: [0] * 3000,repr=False)
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
        valids = set("><+-.,[]")
        left = -1
        for ch in code:
            if ch not in valids:
                continue
            match ch:
                case ">":
                    self.instructions.append(MoveRight(self, index))
                case "<":
                    self.instructions.append(MoveLeft(self, index))
                case "+":
                    self.instructions.append(Increment(self, index))
                case "-":
                    self.instructions.append(Decrement(self, index))
                case ".":
                    self.instructions.append(Write(self, index))
                case ",":
                    self.instructions.append(Read(self, index))
                case "[":
                    self.instructions.append(LoopStart(self, index,-1))
                    left = index
                case "]":
                    self.instructions.append(LoopEnd(self, index, left))
                    assert left != -1, "Unmatched ]"
                    setattr(self.instructions[left], "jump_to", index)
                    left = -1
            index += 1
        assert left == -1, "Unmatched ["

    def run(self):
        index = 0
        cnt = len(self.instructions)
        while (index := self.instructions[index].execute()) < cnt:
            pass
