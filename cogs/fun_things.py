import discord

from config import DiscordConfig
from discord.ext import commands as cmds
from discord.utils import get
from typing import Union
import re

registers = ['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
formats = ['r','i1','i2','i3','j']

# Reusable regex patterns
comment_pattern = re.compile('\#.*')
breakpoint_inline_pattern = re.compile('^\s*(\w+)\:\s*\w+.*$') # Breakpoint is on the same line as the instruction
breakpoint_nextline_pattern = re.compile('^\s*(\w+)\:\s*$') # Breakpoint is only thing on the current line

r_pattern = lambda x: re.compile('^\s*' + x + '\s*\$(\w+)\s*,\s*\$(\w+)\s*,\s*\$(\w+)\s*$')
i1_pattern = lambda x: re.compile('^\s*' + x + '\s*\$(\w+)\s*,\s*(\-?\d+)\s*\(\s*\$(\w+)\s*\)\s*$')
i2_pattern = lambda x: re.compile('^\s*' + x + '\s*\$(\w+)\s*,\s*\$(\w+)\s*,\s*(\w+|\-?\d+)\s*$')
i3_pattern = lambda x: re.compile('^\s*' + x + '\s*\$(\w+)\s*,\s*\$(\w+)\s*,\s*(\w+|\-?\d+)\s*$')
j_pattern = lambda x: re.compile('^\s*' + x + '\s*(\w+|\d+)\s*$')

r_type_opcode = '000000'

commands = {
	'add': {
		'opcode': r_type_opcode,
		'funct': '100000',
		'shampt': '00000',
		'format': 'r'
	},
	'addi': {
		'opcode': '001000',
		'format': 'i3'
	},
	'and': {
		'opcode': r_type_opcode,
		'funct': '100100',
		'shampt': '00000',
		'format': 'r'
	},
	'beq': {
		'opcode': '000100',
		'format': 'i2'
	},
	'bne': {
		'opcode': '000101',
		'format': 'i2'
	},
	'j': {
		'opcode': '000010',
		'format': 'j'
	},
	'lw': {
		'opcode': '100011',
		'format': 'i1'
	},
	'or': {
		'opcode': r_type_opcode,
		'funct': '100101',
		'shampt': '00000',
		'format': 'r'
	},
	'slt': {
		'opcode': r_type_opcode,
		'funct': '101010',
		'shampt': '00000',
		'format': 'r'
	},
	'sw': {
		'opcode': '101011',
		'format': 'i1'
	},
	'sub': {
		'opcode': r_type_opcode,
		'funct': '100010',
		'shampt': '00000',
		'format': 'r'
	}
}


def to_binary(num: int, n: int = 5) -> str:
    '''
    Just convert an integer to binary. Unfortunately, converting a negative number
    invloves a slightly more complicated process since bin() doesn't work on 
    negative numbers.
    '''

    if num < 0:
        # bin() of a negative number returns -thesignednum (bin(-5) => -0b101 instead of 1011)
        # Run the process for multiplying a positive number by -1
        result = bin(num)[3:].zfill(n)

        for i in range(len(result)): # Flip the bits
            if result[i] == '0':
                result = result[:i] + '1' + result[i+1:]
            else:
                result = result[:i] + '0' + result[i+1:]

        # Add 1
        carry = 0
        for i in range(len(result)-1,-1,-1):
            if result[i] == '0' and carry == 0:
                result = result[:i] + '1' + result[i+1:]
                break
            elif result[i] == '1' and carry == 0:
                carry = 1
                result = result[:i] + '0' + result[i+1:]
            elif result[i] == '0' and carry == 1:
                result = result[:i] + '1' + result[i+1:]
                break
            elif result[i] == '1' and carry == 1:
                result = result[:i] + '0' + result[i+1:]
        return result
    else:
        return f'{num:b}'.zfill(n) + ' '


def is_int(s):
    '''
    Check if a string is an integer
    '''

    if len(s) < 1:
        return False
    if s[0] == "-":
        return s[1:].isdigit()
    return s.isdigit()


def translate(instructions):
    '''
    Converts a list of mips instructions into a list of binary strings.
    Returns a list of size 2. The first element is either a 0 or 1. 
    0 indicates the program worked and the correct output is in the second element.
    1 indicates the code wasn't properly formated and an error message is the second element.
    '''

    lines = []
    line_map = {} # Map the original instructions to the new lines in the lines list
    line_num = 1 # Variable for keeping track of errors
    current_line = 0 # The index of the current instruction being parsed

    # Find all breakpoints before parsing the commands
    for line in instructions:
        line = re.sub(comment_pattern, '', line) # Remove comments

        # Ignore empty lines
        if line.strip() == '':
            continue

        inline = re.search(breakpoint_inline_pattern, line)

        if inline:
            breakpoint = inline.groups()[0]
            line_map[breakpoint] = current_line
        else:
            nextline = re.search(breakpoint_nextline_pattern, line)
            if nextline:
                breakpoint = nextline.groups()[0]
                line_map[breakpoint] = current_line
                continue
        
        current_line += 1

    current_line = 0
    for line in instructions:
        unknown_command = True
        line = re.sub(comment_pattern, '', line)

        if line.strip() == '':
            line_num += 1
            continue

        inline = re.search(breakpoint_inline_pattern, line)

        if inline:
            line = re.sub(f'{breakpoint}:', '', line)
        else:
            nextline = re.search(breakpoint_nextline_pattern, line)
            if nextline:
                line_num += 1
                continue

        for key in commands:
            command = commands[key]

            f = command['format'] # format is a Python3 keyword

            if f == 'r':
                pattern = r_pattern(key)
            elif f == 'i1':
                pattern = i1_pattern(key)
            elif f == 'i2':
                pattern = i2_pattern(key)
            elif f == 'i3':
                pattern = i3_pattern(key)
            elif f == 'j':
                pattern = j_pattern(key)

            r = re.search(pattern, line) # Check for an existing pattern
            if r:
                result = command['opcode'] # Line always starts with the opcode
                args = r.groups() # Get the arguments

                if f == 'r':
                    for arg in args:
                        if not arg in registers:
                            return 1, f'Unknown register {arg} on line {line_num}'

                    rs = registers.index(args[1])
                    rt = registers.index(args[2])
                    rd = registers.index(args[0])

                    result += to_binary(rs) + to_binary(rt) + to_binary(rd) + command['shampt'] + command['funct']
                    lines.append(result)
                
                elif f == 'i1':
                    if not args[0] in registers:
                        return 1, f'unknown register {args[0]} on line {line_num}'
                    if not args[2] in registers:
                        return 1, f'unknown register {args[2]} on line {line_num}'

                    rs = registers.index(args[2])
                    rt = registers.index(args[0])

                    immed = int(args[1])
                    result += to_binary(rs) + to_binary(rt) + to_binary(immed, 16)
                    lines.append(result)

                elif f == 'i2':
                    if not args[0] in registers:
                        return 1, f'unknown register {args[0]} on line {line_num}'
                    if not args[1] in registers:
                        return 1, f'unknown register {args[1]} on line {line_num}'

                    rs = registers.index(args[0])
                    rt = registers.index(args[1])

                    immed = args[2]

                    result += to_binary(rs) + to_binary(rt)

                    if is_int(immed): # Check if integer
                        result += to_binary(int(immed), 16)
                    elif immed in line_map:
                        result += to_binary(line_map[immed]-current_line-1, 16) # -1 index because the PC automatically increments (+1 index)
                    else:
                        return 1, 'breakpoint {immed} on line {line_num} does not exist'
                    
                    lines.append(result)

                elif f == 'i3':
                    if not args[0] in registers:
                        return 1, f'unknown register {args[0]} on line {line_num}'
                    if not args[1] in registers:
                        return 1, f'unknown register {args[1]} on line {line_num}'

                    rs = registers.index(args[1])
                    rt = registers.index(args[0])
                    immed = args[2]

                    result += to_binary(rs) + to_binary(rt)

                    if is_int(immed):
                        result += to_binary(int(immed), 16)
                    elif immed in line_map:
                        result += to_binary(line_map[immed] - current_line - 1, 16)
                    else:
                        return 1, f'breakpoint {immed} on line {line_num} does not exist'
                    
                    lines.append(result)
                
                elif f == 'j':
                    addr = args[0]

                    if is_int(addr):
                        result += to_binary(int(addr), 26)
                    elif addr in line_map:
                        result += to_binary(line_map[addr], 26)
                    else:
                        return 1, f'breakpoint {addr} on line {line_num} does not exist'
                    
                    lines.append(result)

                unknown_command = False
                break

        if unknown_command:
            return 1, f'Unknown pattern on line {line_num}'

        line_num += 1
        current_line += 1
        
    return 0, lines


def setup(bot: object) -> None:
    bot.add_cog(FunThings(bot))


class FunThings(cmds.Cog, name = 'FunThings'):
    def __init__(self, bot):
        self.bot = bot

    
    @cmds.command(name = 'mips_to_bin')
    async def mips_to_bin(self, ctx, *mips: str):
        mips_string = ' '.join(mips)

        error, result = translate([mips_string])

        if not error:
            result = result[0] # only the first line

            embed = discord.Embed(title = 'Converted MIPS')
            embed.add_field(name = 'Binary', value = result)

            binary_string = result.replace(' ', '')
            binary = int(binary_string, 2)
            h = hex(binary)

            embed.add_field(name = 'Hex', value = str(h), colour = discord.Colour.green())

            await ctx.send(embed = embed)

        else:
            await ctx.send(result)