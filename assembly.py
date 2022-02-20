from copy import copy
from typing import DefaultDict

class Assembly():
    def __init__(self):
        # External
        self.halt = False

        # Internal
        self.registers = DefaultDict(int)
        self.memory = DefaultDict(int)
        self.labels = DefaultDict(int)

        self.lastCMP = None
        self.marked = None
        self.findingLabel = None

        self.instSet = {"LDR": (["R","M"], self.LDR),
                        "STR": (["R","M"], self.STR),
                        "ADD": (["R","R","O"], self.ADD),
                        "SUB": (["R","R","O"], self.SUB),
                        "MOV": (["R","O"], self.MOV),
                        "CMP": (["R","O"], self.CMP),
                        "AND": (["R","R","O"], self.AND),
                        "ORR": (["R","R","O"], self.ORR),
                        "EOR": (["R","R","O"], self.EOR),
                        "MVN": (["R","O"], self.MVN),
                        "LSL": (["R","R","O"], self.LSL),
                        "LSR": (["R","R","O"], self.LSR),
                        "INP": (["R","A"], self.INP),
                        "OUT": (["R","A"], self.OUT),
                        "HALT": ([], self.HALT)}
        self.branchSet = {"BEQ": (["O"], self.BEQ),
                          "BNE": (["O"], self.BNE),
                          "BGT": (["O"], self.BGT),
                          "BLT": (["O"], self.BLT),
                          "B": (["O"], self.B)}

    def ProcessInstruction(self, instruction, index):
        curInst = instruction.split(" ")
        if self.findingLabel != None:
            if curInst[0][-1] == ":":
                self.WriteLabel(curInst[0][:-1], index)
            return self.FindLabel(self.findingLabel, index)

        if curInst[0] in self.instSet: # Normal Instruction
            inp = [] + curInst[1:]
            if not self.MatchPattern(inp, self.instSet[curInst[0]][0]): 
                raise Exception(f"Instruction: {inp} requires Pattern: {self.instSet[curInst[0]][0]}")
            self.instSet[curInst[0]][1](inp)
            return index + 1
        elif curInst[0] in self.branchSet:
            inp = [] + curInst[1:]
            if not self.MatchPattern(inp, self.branchSet[curInst[0]][0]): 
                raise Exception(f"Instruction: {inp} requires Pattern: {self.branchSet[curInst[0]][0]}")
            out = self.branchSet[curInst[0]][1]([curInst[1]])
            if out: return self.FindLabel(curInst[1], index)
            else: return index + 1
        elif curInst[0][-1] == ":": # Create Label
            self.WriteLabel(curInst[0][:-1], index)
            return index + 1

    def ReadReg(self, R):
        return copy(self.registers[R])
    def WriteReg(self, R, Val):
        self.registers[R] = Val

    def ReadMem(self, R):
        return copy(self.memory[R])
    def WriteMem(self, R, Val):
        self.memory[R] = Val

    def WriteLabel(self, label, index):
        self.labels[label] = index + 1
    def FindLabel(self, label, index):
        if label in self.labels:
            self.findingLabel = None
            self.marked = None
            return self.labels[label]
        elif self.findingLabel == None:
            self.findingLabel = label
            self.marked = index
            return index + 1
        else:
            return index + 1

    def RefVal(self, val):
        if val[0] == "R": 
            return int(val[1:])
        elif val[0].isnumeric(): 
            return int(val)
        else:
            raise Exception(f"Value not Recognisable as a Reference: {val}")
    def ActVal(self, val):
        if val[0] == "R":
            return self.ReadReg(int(val[1:]))
        elif val[0] == "#":
            return int(val[1:])
        elif val.isnumeric(): 
            return self.ReadMem(int(val))
        else:
            raise Exception(f"Actual Value not Recognised: {val}")

    def MatchPattern(self, inp, pattern):
        for i in range(len(pattern)):
            if pattern[i] == "A": pass
            elif pattern[i][0] == "O" and (inp[i][0] == "R" or inp[i][0] == "#"): pass
            elif inp[i][0] == "R" and not pattern[i] == "R": return False
            elif inp[i].isnumeric() and not pattern[i] == "M": return False
            elif inp[i][0] == "#" and not pattern[i] == "N": return False
        return True

    def LDR(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]))
    def STR(self, inp):
        self.WriteMem(self.RefVal(inp[1]), self.ActVal(inp[0]))
    def ADD(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) + self.ActVal(inp[2]))
    def SUB(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) - self.ActVal(inp[2]))
    def MOV(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]))
    def CMP(self, inp):
        self.lastCMP = (self.ActVal(inp[0]), self.ActVal(inp[1]))
    def BEQ(self, inp):
        if self.lastCMP[0] == self.lastCMP[1]: return True
        else: return False
    def BNE(self, inp):
        if self.lastCMP[0] != self.lastCMP[1]: return True
        else: return False
    def BGT(self, inp):
        if self.lastCMP[0] > self.lastCMP[1]: return True
        else: return False
    def BLT(self, inp):
        if self.lastCMP[0] < self.lastCMP[1]: return True
        else: return False
    def B(self, inp):
        return True
    def AND(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) & self.ActVal(inp[2]))
    def ORR(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) | self.ActVal(inp[2]))
    def EOR(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) ^ self.ActVal(inp[2]))
    def MVN(self, inp):
        self.WriteReg(self.RefVal(inp[0]), ~ self.ActVal(inp[1]))
    def LSL(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) << self.ActVal(inp[2]))
    def LSR(self, inp):
        self.WriteReg(self.RefVal(inp[0]), self.ActVal(inp[1]) >> self.ActVal(inp[2]))
    def HALT(self, inp):
        self.halt = True
    def INP(self, inp):
        self.WriteReg(self.RefVal(inp[0]), int(input("Input:")))
    def OUT(self, inp):
        print("Out:", self.ActVal(inp[0]))