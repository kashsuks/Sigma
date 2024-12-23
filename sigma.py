import re
import sys
from typing import Any, Dict, List, Union

class SigmaInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, dict] = {}
        self.inMultilineComment = False

    def parseFile(self, filePath: str) -> None:
        try:
            with open(filePath, 'r') as file:
                code = file.read()
            self.parseAndExecute(code)
        except FileNotFoundError:
            print(f"Error: Could not find Sigma file: {filePath}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    def evaluateMathExpression(self, expr: str) -> Union[int, float]:
        def parseNumber() -> Union[int, float]:
            nonlocal pos
            start = pos
            while pos < len(tokens) and (tokens[pos].isdigit() or tokens[pos] == '.'):
                pos += 1
            return float(tokens[start:pos])

        def parsePower() -> Union[int, float]:
            nonlocal pos
            result = parseFactor()
            
            while pos < len(tokens) and tokens[pos] == '*' and pos + 1 < len(tokens) and tokens[pos + 1] == '*':
                pos += 2
                right = parseFactor()
                result = result ** right
                
            return result

        def parseFactor() -> Union[int, float]:
            nonlocal pos
            
            if pos >= len(tokens):
                raise SyntaxError("Unexpected end of expression")

            if tokens[pos] == '(':
                pos += 1
                result = parseExpression()
                if pos >= len(tokens) or tokens[pos] != ')':
                    raise SyntaxError("Missing closing parenthesis")
                pos += 1
                return result
                
            if tokens[pos].isdigit() or tokens[pos] == '.':
                return parseNumber()
                
            start = pos
            while pos < len(tokens) and (tokens[pos].isalnum() or tokens[pos] in '[]'):
                pos += 1
            varExpr = tokens[start:pos]
            
            arrayMatch = re.match(r'(\w+)\[(\d+)\]', varExpr)
            if arrayMatch:
                arrName = arrayMatch.group(1)
                index = int(arrayMatch.group(2))
                if arrName in self.variables:
                    arr = self.variables[arrName]
                    if isinstance(arr, list):
                        if 0 <= index < len(arr):
                            return float(arr[index])
                        raise IndexError(f"Array index {index} out of bounds")
                    raise TypeError(f"Variable {arrName} is not an array")
            elif varExpr in self.variables:
                return float(self.variables[varExpr])
                
            raise SyntaxError(f"Invalid term in expression: {varExpr}")

        def parseTerm() -> Union[int, float]:
            nonlocal pos
            result = parsePower()
            
            while pos < len(tokens) and tokens[pos] in '*/:':
                op = tokens[pos]
                pos += 1
                right = parsePower()
                
                if op == '*':
                    result *= right
                elif op == '/':
                    if right == 0:
                        raise ZeroDivisionError("Division by zero")
                    result /= right
                    
            return result

        def parseExpression() -> Union[int, float]:
            nonlocal pos
            result = parseTerm()
            
            while pos < len(tokens) and tokens[pos] in '+-':
                op = tokens[pos]
                pos += 1
                right = parseTerm()
                
                if op == '+':
                    result += right
                elif op == '-':
                    result -= right
                    
            return result

        expr = ''.join(expr.split())
        tokens = expr
        pos = 0
        
        result = parseExpression()
        if pos < len(tokens):
            raise SyntaxError(f"Invalid syntax in expression: {expr}")
            
        return result

    def tokenize(self, code: str) -> List[str]:
        lines = []
        for line in code.splitlines():
            line = line.strip()
            if not line or self.inMultilineComment:
                if line.endswith('*/'):
                    self.inMultilineComment = False
                continue
            if line.startswith('/*'):
                self.inMultilineComment = True
                continue
            line = re.sub(r'//.*', '', line)
            if line:
                lines.append(line)
        return lines

    def parseAndExecute(self, code: str) -> None:
        lines = self.tokenize(code)

        if lines[0] != "BEGIN" or lines[-1] != "PERIOD":
            raise SyntaxError("Code must start with BEGIN and end with PERIOD")

        lines = lines[1:-1]

        i = 0
        while i < len(lines):
            line = lines[i]

            if self.inMultilineComment:
                i += 1
                continue

            if line.startswith('rob'):
                i += 1
                continue

            if line.startswith('tweak'):
                funcDef = self.parseFunction(lines[i:])
                i += funcDef['linesConsumed']
                continue

            if line.startswith('call'):
                self.executeFunctionCall(line)

            elif '.asl(' in line:
                self.executeArrayAppend(line)

            elif line.startswith('arrayzler'):
                self.declareArray(line)

            elif any(typeName in line for typeName in ['int', 'bool', 'str', 'float']):
                self.declareVariable(line)

            elif line.startswith('yap'):
                self.executeYap(line)

            i += 1

    def executeArrayAppend(self, line: str) -> None:
        match = re.match(r'(\w+)\.asl\((.*)\)', line)
        if not match:
            raise SyntaxError(f"Invalid array append operation: {line}")
        
        arrName = match.group(1)
        value = match.group(2).strip()
        
        if arrName not in self.variables:
            raise NameError(f"Array '{arrName}' not found")
            
        arr = self.variables[arrName]
        if not isinstance(arr, list):
            raise TypeError(f"Variable '{arrName}' is not an array")
            
        try:
            if isinstance(arr[0], int):
                evalValue = int(self.evaluateMathExpression(value))
            elif isinstance(arr[0], float):
                evalValue = float(self.evaluateMathExpression(value))
            elif isinstance(arr[0], bool):
                evalValue = value.lower() == 'true'
            elif isinstance(arr[0], str):
                evalValue = value.strip('"')
            else:
                raise TypeError(f"Unsupported array type")
                
            arr.append(evalValue)
            self.variables[arrName] = arr
        except Exception as e:
            raise TypeError(f"Value type doesn't match array type: {str(e)}")
    
    def parseFunction(self, lines: List[str]) -> dict:
        firstLine = lines[0]
        match = re.match(r'tweak\s+(\w+)\((\w+):\s*(\w+)\)\s*{', firstLine)
        if not match:
            raise SyntaxError(f"Invalid function definition: {firstLine}")
            
        funcName = match.group(1)
        paramName = match.group(2)
        paramType = match.group(3)
        
        bodyLines = []
        linesConsumed = 1
        
        for line in lines[1:]:
            if line.strip() == '}':
                break
            bodyLines.append(line.strip())
            linesConsumed += 1
        
        self.functions[funcName] = {
            'paramName': paramName,
            'paramType': paramType,
            'body': bodyLines
        }
        
        return {'linesConsumed': linesConsumed + 1}

    def declareArray(self, line: str) -> None:
        match = re.match(r'arrayzler<(\w+)>\s+(\w+)\s*=\s*\[(.*)\]', line)
        if not match:
            raise SyntaxError(f"Invalid array declaration: {line}")
        
        dataType = match.group(1)
        varName = match.group(2)
        values = [v.strip() for v in match.group(3).split(',')]
        try:
            if dataType == 'int':
                array = [int(self.evaluateMathExpression(v)) for v in values]
            elif dataType == 'float':
                array = [float(self.evaluateMathExpression(v)) for v in values]
            elif dataType == 'bool':
                array = [v.lower() == 'true' for v in values]
            elif dataType == 'str':
                array = [v.strip('"') for v in values]
            else:
                raise SyntaxError(f"Unsupported array data type: {dataType}")
        except Exception as e:
            raise SyntaxError(f"Error converting array values to type {dataType}: {str(e)}")
        
        self.variables[varName] = array

    def declareVariable(self, line: str) -> None:
        parts = line.split('=')
        if len(parts) != 2:
            raise SyntaxError(f"Invalid variable declaration: {line}")
            
        varDef = parts[0].strip()
        value = parts[1].strip()
        
        typeName, varName = varDef.split()
        varName = varName.strip()
        
        if typeName in ['int', 'float']:
            try:
                evaluatedValue = self.evaluateMathExpression(value)
                if typeName == 'int':
                    value = int(evaluatedValue)
                else:
                    value = float(evaluatedValue)
            except Exception as e:
                raise SyntaxError(f"Invalid mathematical expression: {value}")
        elif typeName == 'bool':
            value = value.lower() == 'true'
        elif typeName == 'str':
            value = value.strip('"')
            
        self.variables[varName] = value

    def executeYap(self, line: str) -> None:
        match = re.match(r'yap\((\w+(?:\[\d+\])?)\)', line)
        if not match:
            raise SyntaxError(f"Invalid yap statement: {line}")
    
        expr = match.group(1)
        arrayMatch = re.match(r'(\w+)\[(\d+)\]', expr)
        
        if arrayMatch:
            arrName = arrayMatch.group(1)
            index = int(arrayMatch.group(2))
            
            if arrName not in self.variables:
                raise NameError(f"Array '{arrName}' not found")
                
            arr = self.variables[arrName]
            if not isinstance(arr, list):
                raise TypeError(f"Variable '{arrName}' is not an array")
                
            if 0 <= index < len(arr):
                print(arr[index])
            else:
                raise IndexError(f"Array index {index} out of bounds for array {arrName}")
        else:
            varName = expr
            if varName not in self.variables:
                raise NameError(f"Variable '{varName}' not found")
                
            print(self.variables[varName])

    def executeFunctionCall(self, line: str) -> Any:
        match = re.match(r'call\s+(\w+)\((\w+)\)', line)
        if not match:
            raise SyntaxError(f"Invalid function call: {line}")
            
        funcName = match.group(1)
        argName = match.group(2)
        
        if funcName not in self.functions:
            raise NameError(f"Function '{funcName}' not found")
            
        if argName not in self.variables:
            raise NameError(f"Variable '{argName}' not found")
            
        func = self.functions[funcName]
        
        for bodyLine in func['body']:
            executedLine = bodyLine.replace(func['paramName'], argName)
            
            if executedLine.startswith('its giving'):
                return self.executeReturn(executedLine)
            elif executedLine.startswith('yap'):
                self.executeYap(executedLine)
                
    def executeReturn(self, line: str) -> Any:
        match = re.match(r'its\s+giving\s*\((.*)\)', line)
        if not match:
            raise SyntaxError(f"Invalid return statement: {line}")
            
        expr = match.group(1).strip()
        
        try:
            if expr in self.variables:
                return self.variables[expr]
            return self.evaluateMathExpression(expr)
        except:
            return expr.strip('"')

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 sigma.py <filename.sigma>")
        sys.exit(1)
        
    filePath = sys.argv[1]
    if not filePath.endswith('.sigma'):
        print("Error: File must have .sigma extension")
        sys.exit(1)
        
    interpreter = SigmaInterpreter()
    interpreter.parseFile(filePath)

if __name__ == "__main__":
    main()