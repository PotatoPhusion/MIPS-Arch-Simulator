from sys import argv
import math


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
    arg1 = []           # list of all first args in order of instructions (-1 = N/A)
    arg2 = []           # list of all second args in order of instructions (-1 = N/A)
    arg3 = []           # list of all third args in order of instructions (-1 = N/A)
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
        return (int(binString[1:], 2) - ((2 * int(binString[0], 2)) ** (len(binString) - 1)))

    #############
    # Disassembles the list of binary strings
    def disassemble(self):
        breakFound = False

        for i in range(len(self.binaryList)):
            if (breakFound == False):
                self.numInstrs += 1
                self.instructions.append(self.binaryList[i])

                breakFound = self.determineInstruction(self.binaryList[i])
                self.instStrings.append(self.toString(self.binaryList[i]))
            else:
                self.mem.append(self.twosComp(self.binaryList[i]))
    
    ############
    # Breaks up the instruction and stores it in the appropriate list
    #
    # Returns TRUE if break instruction was found
    def determineInstruction(self, inst):

        if (int(inst[:1], 2) == 0):
            self.valids.append(0)
            return False

        opcode = int(inst[1:6], 2)
        self.opcodes.append(opcode)
        
        if (opcode == 0 or opcode == 28):
            self.arg1.append(int(inst[6:11], 2))
            self.arg2.append(int(inst[11:16], 2))
            self.arg3.append(int(inst[16:21], 2))

            functionCode = int(inst[-6:], 2)

            # BREAK found
            if (functionCode == 13):
                return True
        
        elif (opcode == 2):
            self.arg1.append(-(int(inst[6:11], 2)))
            self.arg2.append(-(int(inst[11:16], 2)))
            self.arg3.append(-(int(inst[16:21], 2)))

        else:
            self.arg1.append(int(inst[6:11], 2))
            self.arg2.append(int(inst[11:16], 2))
            self.arg3.append(int(inst[16:], 2))

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
# Variables
#========================================
PC = 96

#========================================
# Function Definitions
#========================================






def disOutput(disFile, binary, PC, instString, doSpacing):
    fullLine = binary
    if (doSpacing):
        fullLine = binary[0] + " " + binary[1:6] + " " + binary[6:11] + " " + binary[11:16] + " "
        fullLine += binary[16:21] + " " + binary[21:26] + " " + binary[26:]
    
    if (instString != "data"):
        fullLine += "\t" + str(PC)
        fullLine += "\t" + instString
    else:
        fullLine += "\t" + str(PC)
        fullLine += "\t" + str(twosComp(binary, 32))

    disFile.write(fullLine + "\n")


#========================================
# Main Code
#========================================
for i in range(len(argv)):
    if (argv[i] == '-i' and i < (len(argv) - 1)):  # make sure there are at least 2 args
        inputFileName = argv[i + 1]		    
    elif (argv[i] == '-o' and i < (len(argv) - 1)):
        outputFileName = argv[i + 1]

inFile = open(inputFileName, "r")
disFile = open(outputFileName + "_dis.txt", "w")
#pipelineFile = open(outputFileName + "_pipeline.txt", "w")

instructions = inFile.readlines()

dis = Disassembler(instructions)
dis.disassemble()
dis.output(disFile)

inFile.close()
disFile.close()




