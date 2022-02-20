from assembly import *

with open(input(), 'r') as f:
    instructions = [l.strip() for l in f.readlines()]

lang = Assembly()
index = 0
while not lang.halt:
    if index >= len(instructions) and lang.findingLabel != None:
        raise Exception(f"Label: {lang.findingLabel} not found")
    index = lang.ProcessInstruction(copy(instructions[index]), index)