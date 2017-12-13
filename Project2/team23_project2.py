from sys import argv
import math

mainMemory = []
registers = [0] * 33

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
                self.valids.append(int(self.binaryList[i][:1], 2))
                self.addrs.append(PC)
                self.mem.append(self.twosComp(self.binaryList[i]))
                PC += 4
    
    ############
    # Breaks up the instruction and stores it in the appropriate list
    #
    # Returns TRUE if break instruction was found
    def determineInstruction(self, inst, PC):

        if (int(inst[:1], 2) == 0):
            self.valids.append(0)
            return False

        self.valids.append(1)
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
# Fetch Class
#========================================
class Fetch:

    preIssueBuffer = [-1, -1, -1, -1]

    def __init__(self, _cache):
        self.cache = _cache
        
    def run(self):
        index = (Simulator.PC - 96) / 4
        isHit, word = self.cache.accessMem(index, 0, False, 0);
        if (isHit):
            for i in range(len(self.preIssueBuffer)):
                if (self.preIssueBuffer[i] == -1):
                    self.preIssueBuffer[i] = index
                    Simulator.PC += 4
                    if (int(word[1:6], 2) == 0 and int(word[-6:], 2) == 13):
                        # BREAK Found
                        return False # Placeholder
                    break
        else:
            return True
        return True

#========================================
# ALU Class
#========================================
class LogicUnit:

    preALUBuff = [-1, -1]
    postALUBuff = [-1, -1]      # value, register

    def __init__(self, instructions, opcode, args1, args2, args3):
        self.instructions = instructions
        self.opcode = opcode
        self.args1 = args1
        self.args2 = args2
        self.args3 = args3

    def advanceBuffer(self):
        self.preALUBuff[0] = self.preALUBuff[1]
        self.preALUBuff[1] = -1

    def run(self):
        index = self.preALUBuff[0]
        if (self.preALUBuff[0] != -1):
            if (self.opcode[index] == 0 and (int(self.instructions[index], 2)& 63) == 32):   # ADD
                self.postALUBuff = [self.args1[index] + self.args2[index], self.args3[index]]
                self.advanceBuffer()
            elif (self.opcode[index] == 8):                                                  # ADDI
                self.postALUBuff = [self.args1[index] + self.args3[index], self.args2[index]]
                self.advanceBuffer()

#========================================
# Memory Class
#========================================
class MemoryUnit:
    def run(self):
        return

#========================================
# WriteBack Class
#========================================
class WriteBack:
    def run(self, postALUBuff):
        registers[postALUBuff[1]] = postALUBuff[0]

#========================================
# Issue Class
#========================================
class Issue:

    def adjustBuffer(self):
        for i in range(len(Fetch.preIssueBuffer) - 1):
            Fetch.preIssueBuffer[i] = Fetch.preIssueBuffer[i + 1]
            Fetch.preIssueBuffer[i + 1] = -1

    def run(self):
        if (Fetch.preIssueBuffer[0] != -1):
            if (LogicUnit.preALUBuff[0] == -1):
                LogicUnit.preALUBuff[0] = Fetch.preIssueBuffer[0]
                self.adjustBuffer()
            elif (LogicUnit.preALUBuff[1] == -1):
                LogicUnit.preALUBuff[1] = Fetch.preIssueBuffer[0]
                self.adjustBuffer()

#========================================
# Cache Class
#========================================
class Cache:

    # valid, dirty, tag, data, data
    cacheSets = [[[0,0,0,0,0], [0,0,0,0,0]],
                 [[0,0,0,0,0], [0,0,0,0,0]],
                 [[0,0,0,0,0], [0,0,0,0,0]],
                 [[0,0,0,0,0], [0,0,0,0,0]]]

    lruBit = [0,0,0,0]

    justMissedList = []

    def accessMem(self, memIndex, instructionIndex, isWriteToMem, dataToWrite):
        address = 96 + (memIndex * 4)

        if (address % 8 == 0):
            dataWord = 0
            address1 = address
            address2 = address + 4
        if (address % 8 != 0):
            dataWord = 1
            address1 = address - 4
            address2 = address

        data1 = mainMemory[(address1 - 96) / 4]
        data2 = mainMemory[(address2 - 96) / 4]

        if (memIndex != -1 and isWriteToMem == True):
            if (dataWord == 0):
                data1 = dataToWrite
            elif (dataWord == 1):
                data2 = dataToWrite

        set = address & 24
        set = set >> 3
        tag = address >> 5

        cacheTag = self.cacheSets[set][self.lruBit[set]][2]     # 3rd element contains the tag
        tempAddress = (dataWord << 2) + (cacheTag << 5) + (set << 3)

        if (address == tempAddress):    # Cache Hit
            if (not isWriteToMem):
                self.lruBit[set] = 1
                return True, self.cacheSets[set][self.lruBit[set]][3 + dataWord]    # Offset for requested word
        else:                           # Cache Miss
            for k in range(len(self.justMissedList)):
                if (address == self.justMissedList[k]):      # Second Miss
                    lru = 5
                    overwriteIndex = 0
                    for i in range(len(self.lruBit)):
                        if (self.lruBit[i] < lru):
                            lru = self.lruBit[i]
                            overwriteIndex = i
                    if (self.cacheSets[set][self.lruBit[set]][1] == 1):
                        wbAddr = self.cacheSets[set][self.lruBit[set]][2]   # tag
                        wbAddr = (wbAddr << 5) + (set << 3)                 # Revert to address

                        # Store last season's data in memory
                        if (wbAddr >= (Simulator.numInstructions * 4) + 96):
                            mainMemory[(wbAddr - 96) / 4] = self.cacheSets[set][self.lruBit[set]][3]
                        if (wbAddr + 4 >= (Simulator.numInstructions * 4) + 96):
                            mainMemory[(wbAddr - 92) / 4] = self.cacheSets[set][self.lruBit[set]][4]

                    # Put the fresh, juicy data into cache
                    self.cacheSets[set][self.lruBit[set]][0] = 1        # Valid: we are writing a block
                    self.cacheSets[set][self.lruBit[set]][1] = 0        # reset the dirty bit
                    if (isWriteToMem):
                        self.cacheSets[set][self.lruBit[set]][1] = 1    # dirty if data mem is dirty again, INSTRUCTIONS ARE NEVER DIRTY
                    self.cacheSets[set][self.lruBit[set]][2] = tag      # update the tag
                    self.cacheSets[set][self.lruBit[set]][3] = data1    # update the first word
                    self.cacheSets[set][self.lruBit[set]][4] = data2    # update the second word
                    self.lruBit[set] = (self.lruBit[set] + 1) % 2       # set LRU to show block is recently used

                    # Finally
                    return True, self.cacheSets[set][(self.lruBit[set] + 1) % 2][dataWord + 3]  # dataWord was the actual word that
                                                                                                # generated the hit
            self.justMissedList.append(address)               # First miss
            return False, 0
                    
                

        return False, 0

    def flush(self):
        return
        
#========================================
# Simulator Class
#========================================
class Simulator:

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
    PC = 96

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
        self.ALU = LogicUnit(insts, opcodes, args1, args2, args3)


    


    issue = Issue()
    
    MEM = MemoryUnit()
    WB = WriteBack()
    cache = Cache()
    fetch = Fetch(cache)
    dis = Disassembler(instructions)

    

    #****************************************************
    # Prints all information about the state of the
    # entire machine at the moment the function is called
    #****************************************************
    def printState(self):
        pipelineFile.write("--------------------\n")
        pipelineFile.write("Cycle:" + str(self.cycle) + '\n')

        pipelineFile.write("\nPre-Issue Buffer:\n")
        pipelineFile.write("\tEntry 0:\t")
        if (Fetch.preIssueBuffer[0] != -1):
            pipelineFile.write(self.dis.toString(self.instructions[Fetch.preIssueBuffer[0]]))
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 1:\t")
        if (Fetch.preIssueBuffer[1] != -1):
            pipelineFile.write(self.dis.toString(self.instructions[Fetch.preIssueBuffer[1]]))
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 2:\t")
        if (Fetch.preIssueBuffer[2] != -1):
            pipelineFile.write(self.dis.toString(self.instructions[Fetch.preIssueBuffer[2]]))
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 3:\t")
        if (Fetch.preIssueBuffer[3] != -1):
            pipelineFile.write(self.dis.toString(self.instructions[Fetch.preIssueBuffer[3]]))
        pipelineFile.write('\n')

        pipelineFile.write("Pre_ALU Queue:\n")
        pipelineFile.write("\tEntry 0:\t")
        if (LogicUnit.preALUBuff[0] != -1):
            pipelineFile.write(self.dis.toString(self.instructions[LogicUnit.preALUBuff[0]]))
        pipelineFile.write('\n')
        pipelineFile.write("\tEntry 1:\t")
        if (LogicUnit.preALUBuff[1] != -1):
            pipelineFile.write(self.dis.toString(self.instructions[LogicUnit.preALUBuff[1]]))
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
            pipelineFile.write(str(registers[i]) + "\t")
        pipelineFile.write("\n")

        pipelineFile.write("R08:\t")
        for i in range(8, 16):
            pipelineFile.write(str(registers[i]) + "\t")
        pipelineFile.write("\n")

        pipelineFile.write("R16:\t")
        for i in range(16, 24):
            pipelineFile.write(str(registers[i]) + "\t")
        pipelineFile.write("\n")

        pipelineFile.write("R24:\t")
        for i in range(24, 32):
            pipelineFile.write(str(registers[i]) + "\t")
        pipelineFile.write("\n\n")

        ##### Cache Output #####
        pipelineFile.write("Cache\n")
        pipelineFile.write("Set 0: LRU=")
        pipelineFile.write(str(Cache.lruBit[0]))
        pipelineFile.write("\n\tEntry 0:")
        pipelineFile.write("[(" + str(Cache.cacheSets[0][0][0]) + "," +
                           str(Cache.cacheSets[0][0][1]) + "," +
                           str(Cache.cacheSets[0][0][2]) + ")<" +
                           str(Cache.cacheSets[0][0][3]) + "," +
                           str(Cache.cacheSets[0][0][4]) + ">]")
        pipelineFile.write("\n\tEntry 1:")
        pipelineFile.write("[(" + str(Cache.cacheSets[0][1][0]) + "," +
                           str(Cache.cacheSets[0][1][1]) + "," +
                           str(Cache.cacheSets[0][1][2]) + ")<" +
                           str(Cache.cacheSets[0][1][3]) + "," +
                           str(Cache.cacheSets[0][1][4]) + ">]")
        pipelineFile.write("\nSet 1: LRU=")
        pipelineFile.write(str(Cache.lruBit[1]))
        pipelineFile.write("\n\tEntry 0:")
        pipelineFile.write("[(" + str(Cache.cacheSets[1][0][0]) + "," +
                           str(Cache.cacheSets[1][0][1]) + "," +
                           str(Cache.cacheSets[1][0][2]) + ")<" +
                           str(Cache.cacheSets[1][0][3]) + "," +
                           str(Cache.cacheSets[1][0][4]) + ">]")
        pipelineFile.write("\n\tEntry 1:")
        pipelineFile.write("[(" + str(Cache.cacheSets[1][1][0]) + "," +
                           str(Cache.cacheSets[1][1][1]) + "," +
                           str(Cache.cacheSets[1][1][2]) + ")<" +
                           str(Cache.cacheSets[1][1][3]) + "," +
                           str(Cache.cacheSets[1][1][4]) + ">]")
        pipelineFile.write("\nSet 2: LRU=")
        pipelineFile.write(str(Cache.lruBit[2]))
        pipelineFile.write("\n\tEntry 0:")
        pipelineFile.write("[(" + str(Cache.cacheSets[2][0][0]) + "," +
                           str(Cache.cacheSets[2][0][1]) + "," +
                           str(Cache.cacheSets[2][0][2]) + ")<" +
                           str(Cache.cacheSets[2][0][3]) + "," +
                           str(Cache.cacheSets[2][0][4]) + ">]")
        pipelineFile.write("\n\tEntry 1:")
        pipelineFile.write("[(" + str(Cache.cacheSets[2][1][0]) + "," +
                           str(Cache.cacheSets[2][1][1]) + "," +
                           str(Cache.cacheSets[2][1][2]) + ")<" +
                           str(Cache.cacheSets[2][1][3]) + "," +
                           str(Cache.cacheSets[2][1][4]) + ">]")
        pipelineFile.write("\nSet 3: LRU=")
        pipelineFile.write(str(Cache.lruBit[3]))
        pipelineFile.write("\n\tEntry 0:")
        pipelineFile.write("[(" + str(Cache.cacheSets[3][0][0]) + "," +
                           str(Cache.cacheSets[3][0][1]) + "," +
                           str(Cache.cacheSets[3][0][2]) + ")<" +
                           str(Cache.cacheSets[3][0][3]) + "," +
                           str(Cache.cacheSets[3][0][4]) + ">]")
        pipelineFile.write("\n\tEntry 1:")
        pipelineFile.write("[(" + str(Cache.cacheSets[3][1][0]) + "," +
                           str(Cache.cacheSets[3][1][1]) + "," +
                           str(Cache.cacheSets[3][1][2]) + ")<" +
                           str(Cache.cacheSets[3][1][3]) + "," +
                           str(Cache.cacheSets[3][1][4]) + ">]")
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
        self.PC = 96
        while go:
            self.WB.run(LogicUnit.postALUBuff)
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


mainMemory = inFile.readlines()

# Trim new line characters off of strings
for i in range(len(mainMemory)):
    mainMemory[i] = mainMemory[i][:32]

dis = Disassembler(mainMemory)
dis.disassemble()
dis.output(disFile)

sim = Simulator(dis.binaryList, dis.opcodes, dis.mem, dis.valids,
                dis.addrs, dis.args1, dis.args2, dis.args3, dis.numInstrs)

sim.run()

inFile.close()
disFile.close()
pipelineFile.close()




