from sys import argv
import math

#========================================
# Command Line Arguments
#========================================
for i in range(len(argv)):
    if (argv[i] == '-i' and i < (len(argv) - 1)):  # make sure there are at least 2 args
        inputFileName = argv[i + 1]		    
    elif (argv[i] == '-o' and i < (len(argv) - 1)):
        outputFileName = argv[i + 1]

inFile = open(inputFileName, "r")
disFile = open(outputFileName + "_dis.txt", "w")
pipelineFile = open(outputFileName + "_pipeline.txt", "w")

#========================================
# Disassembler Class
#========================================
class Disassembler:

    binaryList = []

    instructions = []   # the list of all INSTRUCTIONS, without data
    opcodes = []        # the opcode of every instruction in order
    mem = []            # values stored in memory after the BREAK instruction
    valids = []         # indecies of valid instructions
    addrs = []          # addresses of the instructions in their respective order
    args1 = []          # list of all first args in order of instructions (-1 = N/A)
    args2 = []          # list of all second args in order of instructions (-1 = N/A)
    args3 = []          # list of all third args in order of instructions (-1 = N/A)
                        # arg3 INCLUDES IMMEDIATE VALUES
    instStrings = []    # the formatted string of the instruction

    numInstrs = 0       # the total number of instructions



    def __init__(self, binaryList):
        # Trim new line characters off of strings
        for i in range(len(binaryList)):
            self.binaryList.append(binaryList[i][:32])
    
    #############
    # Evaluates the 2's Complement form of a binary number
    def twosComp(self, binString):
        return (int(binString[1:], 2) - ((int(binString[0], 2)) << (len(binString) - 1)))

    #############
    # Disassembles the list of binary strings
    def disassemble(self):
        breakFound = False
        PC = 96

        for i in range(len(self.binaryList)):
            if (breakFound == False):
                breakFound = self.determineInstruction(self.binaryList[i], PC)
                self.instStrings.append(self.toString(self.binaryList[i]))
                PC += 4
            else:
                self.mem.append(self.twosComp(self.binaryList[i]))
    
    ############
    # Breaks up the instruction and stores it in the appropriate list
    #
    # Returns TRUE if break instruction was found
    def determineInstruction(self, inst, PC):

        if (int(inst[:1], 2) == 0):
            self.valids.append(0)
            return False

        self.addrs.append(PC)
        self.instructions.append(inst)
        self.numInstrs += 1
        opcode = int(inst[1:6], 2)
        self.opcodes.append(opcode)
        
        if (opcode == 0 or opcode == 28):
            self.args1.append(int(inst[6:11], 2))
            self.args2.append(int(inst[11:16], 2))
            self.args3.append(int(inst[16:21], 2))

            functionCode = int(inst[-6:], 2)

            # BREAK found
            if (functionCode == 13):
                return True
        
        elif (opcode == 2):
            self.args1.append(-(int(inst[6:11], 2)))
            self.args2.append(-(int(inst[11:16], 2)))
            self.args3.append(-(int(inst[16:21], 2)))

        else:
            self.args1.append(int(inst[6:11], 2))
            self.args2.append(int(inst[11:16], 2))
            self.args3.append(self.twosComp(inst[16:]))

        return False

    ############
    # returns the binary instruction as a formatted string
    def toString(self, inst):
        instString = " "

        # determine opcode
        opcode = int(inst[1:6], 2)


        if (int(inst, 2) == 0):
            instString = "NOP"

        # r-types
        elif (opcode == 0 or opcode == 28):

            # gather all parts of instruction for R-Types
            rs = "R" + str(int(inst[6:11], 2))
            rt = "R" + str(int(inst[11:16], 2))
            rd = "R" + str(int(inst[16:21], 2))
            functionCode = int(inst[-6:], 2)

            # MUL
            if (opcode == 28 and functionCode == 2):
                instString = "MUL\t" + rd + ", " + rs + ", " + rt
            # JR
            elif (functionCode == 8):
                instString = "JR\t" + rs
            # ADD
            elif (functionCode == 32):
                instString = "ADD\t" + rd + ", " + rs + ", " + rt
            # SUB
            elif (functionCode == 34):
                instString = "SUB\t" + rd + ", " + rs + ", " + rt
            # SLL
            elif (functionCode == 0):
                shiftAmount = str(int(inst[21:26], 2))
                instString = "SLL\t" + rd + ", " + rt + ", #" + shiftAmount
            # SRL
            elif (functionCode == 2):
                shiftAmount = str(int(inst[21:26], 2))
                instString = "SRL\t" + rd + ", " + rt + ", #" + shiftAmount
            # AND
            elif (functionCode == 36):
                instString = "AND\t" + rd + ", " + rs + ", " + rt
            # OR
            elif (functionCode == 37):
                instString = "OR\t" + rd + ", " + rs + ", " + rt
            # MOVZ
            elif (functionCode == 10):
                instString = "MOVZ\t" + rd + ", " + rs + ", " + rt
            # BREAK
            elif (functionCode == 13):
                instString = "BREAK"

        # j-types
        elif (opcode == 2):
            addr = str(int(inst[6:], 2) * 4)
            instString = "J\t#" + addr

        # i-types
        else:

            # gather all parts of instruction for I-Types
            rs = "R" + str(int(inst[6:11], 2))
            rt = "R" + str(int(inst[11:16], 2))
            imm = str(self.twosComp(inst[16:]))

            # BEQ
            if (opcode == 4):
                offset = int(imm)
                instString = "BEQ\t" + rs + ", " + rt + ", #" + str(offset)
            # BLTZ
            elif (opcode == 1):
                offset = int(imm)
                instString = "BLTZ\t" + rs + ", #" + str(offset)
            # ADDI
            elif (opcode == 8):
                instString = "ADDI\t" + rt + ", " + rs + ", #" + imm
            # SW
            elif (opcode == 11):
                instString = "SW\t" + rt + ", " + imm + "(" + rs + ")"
            # LW
            elif (opcode == 3):
                instString = "LW\t" + rt + ", " + imm + "(" + rs + ")"


        # Return
        return instString

    def output(self, file):
        PC = 96
        index = 0;
        for i in range(len(self.instructions)):
            fullLine = self.instructions[i][0] + " " + self.instructions[i][1:6] + " "
            fullLine += self.instructions[i][6:11] + " " + self.instructions[i][11:16] + " "
            fullLine += self.instructions[i][16:21] + " " + self.instructions[i][21:26] + " " 
            fullLine += self.instructions[i][26:]

            fullLine += "\t" + str(PC)
            fullLine += "\t" + self.instStrings[i]

            file.write(fullLine + "\n")

            PC += 4
            index += 1
        for i in range(len(self.mem)):
            fullLine = str(self.binaryList[index])

            fullLine += "\t" + str(PC)
            fullLine += "\t" + str(self.mem[i])

            file.write(fullLine + "\n")

            PC += 4
            index += 1

        
#========================================
# Simulator Class
#========================================
class Simulator:

    class Fetch:
        def __init__(self):
            print "Init Fetch"
        def run(self):
            print "Run Fetch"
            return False

    class Issue:
        def run(self):
            print "Run Issue"

    class LogicUnit:
        def run(self):
            print "Run ALU"

    class MemoryUnit:
        def run(self):
            print "Run MemoryUnit"

    class WriteBack:
        def run(self):
            print "Run WriteBack Unit"


    fetch = Fetch()
    issue = Issue()
    ALU = LogicUnit()
    MEM = MemoryUnit()
    WB = WriteBack()

    registers = [0] * 32
    instructions = []
    opcodes = []
    memory = []
    valids = []
    addresses = []
    numInstructions = []
    args1 = []
    args2 = []
    args3 = []

    numInstructions = 0
    cycle = 1


    #****************************************************
    # Constructor for the Simulator Class
    #****************************************************
    def __init__(self, insts, opcodes, mem, valids, addrs, args1, args2, args3, numInstrs):
        self.instructions = insts
        self.opcodes = opcodes
        self.memory = mem
        self.valids = valids
        self.addresses = addrs
        self.numInstructions = numInstrs
        self.args1 = args1
        self.args2 = args2
        self.args3 = args3

    #****************************************************
    # Prints all information about the state of the
    # entire machine at the moment the function is called
    #****************************************************
    def printState(self):
        pipelineFile.write("--------------------\n")
        pipelineFile.write("Cycle:" + str(self.cycle) + '\n')

        pipelineFile.write("\nPre-Issue Buffer:\n")
        pipelineFile.write("\tEntry 0:\t")
        # Buffer 0 contents go here
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 1:\t")
        # Buffer 1 contents go here
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 2:\t")
        # Buffer 2 contents go here
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 3:\t")
        # Buffer 3 contents go here
        pipelineFile.write('\n')

        pipelineFile.write("Pre_ALU Queue:\n")
        pipelineFile.write("\tEntry 0:\t")
        # Entry 0 goes here
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 1:\t")
        # Entry 1 goes here
        pipelineFile.write('\n')

        pipelineFile.write("Post_ALU Queue:\n")
        pipelineFile.write("\tEntry 0:\t")
        # Entry 0 contents go here
        pipelineFile.write('\n')

        pipelineFile.write("Pre_MEM Queue:\n")
        pipelineFile.write("\tEntry 0:\t")
        # Entry 0 contents go here
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 1:\t")
        # Entry 1 contents go here
        pipelineFile.write('\n')

        pipelineFile.write("Post_MEM Queue:\n")
        pipelineFile.write("\tEntry 0:\t")
        # Entry 0 contents go here
        pipelineFile.write("\n\n")

        ##### Register output #####
        pipelineFile.write("Registers\n")
        pipelineFile.write("R00:\t")
        for i in range(8):
            pipelineFile.write(str(self.registers[i]) + "\t")
        pipelineFile.write("\n")

        pipelineFile.write("R08:\t")
        for i in range(8, 16):
            pipelineFile.write(str(self.registers[i]) + "\t")
        pipelineFile.write("\n")

        pipelineFile.write("R16:\t")
        for i in range(16, 24):
            pipelineFile.write(str(self.registers[i]) + "\t")
        pipelineFile.write("\n")

        pipelineFile.write("R24:\t")
        for i in range(24, 32):
            pipelineFile.write(str(self.registers[i]) + "\t")
        pipelineFile.write("\n\n")

        ##### Cache Output #####
        pipelineFile.write("Cache\n")
        pipelineFile.write("Set 0: LRU=")
        # LRU value goes here
        pipelineFile.write("\n\tEntry 0:")
        # Cache info goes here
        pipelineFile.write("\n\tEntry 1:")
        # Cache info goes here
        pipelineFile.write("\nSet 1: LRU=")
        # LRU value goes here
        pipelineFile.write("\n\tEntry 0:")
        # Cache info goes here
        pipelineFile.write("\n\tEntry 1:")
        # Cache info goes here
        pipelineFile.write("\nSet 2: LRU=")
        # LRU value goes here
        pipelineFile.write("\n\tEntry 0:")
        # Cache info goes here
        pipelineFile.write("\n\tEntry 1:")
        # Cache info goes here
        pipelineFile.write("\nSet 3: LRU=")
        # LRU value goes here
        pipelineFile.write("\n\tEntry 0:")
        # Cache info goes here
        pipelineFile.write("\n\tEntry 1:")
        # Cache info goes here
        pipelineFile.write("\n\n")

        ##### Data Output #####
        pipelineFile.write("Data")
        for i in range(len(self.memory)):
            if (i % 8 == 0):
                pipelineFile.write('\n')
                pipelineFile.write(str(self.addresses[len(self.addresses) - 1]) + ":\t")
            pipelineFile.write(str(self.memory[i]) + '\t')
        pipelineFile.write('\n')

    def run(self):
        go = True
        while go:
            self.WB.run()
            self.ALU.run()
            self.MEM.run()
            self.issue.run()
            go = self.fetch.run()
            self.printState()
            self.cycle += 1
    

#========================================
# Function Definitions
#========================================


#========================================
# Main Code
#========================================


instructions = inFile.readlines()

dis = Disassembler(instructions)
dis.disassemble()
dis.output(disFile)

sim = Simulator(dis.instructions, dis.opcodes, dis.mem, dis.valids,
                dis.addrs, dis.args1, dis.args2, dis.args3, dis.numInstrs)

sim.run()

inFile.close()
disFile.close()
pipelineFile.close()




