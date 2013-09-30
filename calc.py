#TODO:
# +Allow binary, octal, and hexadecimal operations
# +Add flags to change output format, i.e. /b /o /d /h (or /x)
# -Add protection from expressions that take more than like 1 second to evaluate
# +Make it so output wont be returned if it's longer than 400 characters
# +Add protection from code injection - i.e. .calc bot_config

def checkSize(value):
    #won't return calculated value if it spans more than one IRC message
    if len(str(value)) > 350:
        return "It's probably fuck you"
    else:
        return value

def calc(expression):
    output_mode = "dec"
    value = 0
    
    #flags for changing output mode    
    if expression[0] == "/":
        if expression[1] == "b":
            output_mode = "bin"
        elif expression[1] == "o":
            output_mode = "oct"
        elif expression[1] == "h" or expression[1] == "x":
            output_mode = "hex"
        expression = expression[3:]

    try:
        value = eval(expression)
        int(value) #if it's returning something that isnt a number, not good!
    except:
        return "It's probably fuck you"
        
    if output_mode == "bin":
        return checkSize( bin(int(value)) )
    elif output_mode == "oct":
        return checkSize( oct(int(value)) )
    elif output_mode == "dec":
        return checkSize( value )
    elif output_mode == "hex":
        return checkSize( hex(int(value)) )
