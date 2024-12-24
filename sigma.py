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

            if '=' in line:
                if any(typeName in line for typeName in ['int', 'bool', 'str', 'float']):
                    self.declareVariable(line)
                else:
                    self.executeAssignment(line)
            elif line.startswith('call'):
                self.executeFunctionCall(line)
            elif '.asl(' in line:
                self.executeArrayAppend(line)
            elif line.startswith('arrayzler'):
                self.declareArray(line)
            elif line.startswith('yap'):
                self.executeYap(line)

            i += 1
    
    def executeAssignment(self, line: str) -> None:
        parts = line.split('=')
        if len(parts) != 2:
            raise SyntaxError(f"Invalid assignment: {line}")
        
        varName = parts[0].strip()
        value = parts[1].strip()
        
        if varName not in self.variables:
            raise NameError(f"Variable '{varName}' not found")
        
        currentValue = self.variables[varName]
        try:
            evaluatedValue = self.evaluateMathExpression(value)
            if isinstance(currentValue, int):
                value = int(evaluatedValue)
            elif isinstance(currentValue, float):
                value = float(evaluatedValue)
            elif isinstance(currentValue, bool):
                value = value.lower() == 'true'
            elif isinstance(currentValue, str):
                value = value.strip('"')
        except Exception as e:
            raise TypeError(f"Invalid value type for assignment: {value}")
        
        self.variables[varName] = value

    def handleFunctionAssignment(self, line: str) -> None:
        parts = line.split('=')
        if len(parts) != 2:
            raise SyntaxError(f"Invalid function assignment: {line}")
            
        varDef = parts[0].strip()
        funcCall = parts[1].strip()
        
        typeName, varName = varDef.split()
        varName = varName.strip()
        
        result = self.executeFunctionCall(funcCall)
        
        if typeName == 'int':
            self.variables[varName] = int(result)
        elif typeName == 'float':
            self.variables[varName] = float(result)
        elif typeName == 'bool':
            self.variables[varName] = bool(result)
        elif typeName == 'str':
            self.variables[varName] = str(result)
        else:
            raise TypeError(f"Unsupported return type: {typeName}")
    
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
        match = re.match(r'tweak\s+(\w+)\s*\((.*?)\)\s*{', firstLine)
        if not match:
            raise SyntaxError(f"Invalid function definition: {firstLine}")
            
        funcName = match.group(1)
        params = match.group(2).strip()
        
        paramDict = {}
        if params:
            param_parts = params.split(':')
            if len(param_parts) != 2:
                raise SyntaxError(f"Invalid parameter format: {params}")
            paramDict = {
                'paramName': param_parts[0].strip(),
                'paramType': param_parts[1].strip()
            }
        
        bodyLines = []
        linesConsumed = 1
        
        for line in lines[1:]:
            if line.strip() == '}':
                break
            bodyLines.append(line.strip())
            linesConsumed += 1
        
        self.functions[funcName] = {
            'params': paramDict,
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
        
        try:
            evaluatedValue = self.evaluateMathExpression(value)
            if typeName == 'int':
                value = int(evaluatedValue)
            elif typeName == 'float':
                value = float(evaluatedValue)
            elif typeName == 'bool':
                value = value.lower() == 'true'
            elif typeName == 'str':
                value = value.strip('"')
        except Exception as e:
            raise SyntaxError(f"Invalid value for type {typeName}: {value}")
                
        self.variables[varName] = value

    def executeYap(self, line: str) -> None:
        match = re.match(r'yap\((.*)\)', line)
        if not match:
            raise SyntaxError(f"Invalid yap statement: {line}")

        expr = match.group(1).strip()
        
        if expr.startswith('call'):
            result = self.executeFunctionCall(expr)
            print(result)
            return
            
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
                
        elif expr.startswith('"') and expr.endswith('"'):
            print(expr.strip('"'))
            
        elif expr.replace('.','',1).isdigit():
            print(float(expr) if '.' in expr else int(expr))
            
        elif expr in self.variables:
            print(self.variables[expr])
            
        else:
            try:
                result = self.evaluateMathExpression(expr)
                print(int(result) if result.is_integer() else result)
            except:
                raise NameError(f"Invalid expression in yap statement: {expr}")

    def executeFunctionCall(self, line: str) -> Any:
        match = re.match(r'call\s+(\w+)\((.*?)\)', line)
        if not match:
            raise SyntaxError(f"Invalid function call: {line}")
            
        funcName = match.group(1)
        argName = match.group(2).strip()
        
        if funcName not in self.functions:
            raise NameError(f"Function '{funcName}' not found")
            
        func = self.functions[funcName]
        
        returnValue = None
        for bodyLine in func['body']:
            if func['params']:
                if not argName:
                    raise SyntaxError(f"Function '{funcName}' requires an argument")
                if argName not in self.variables:
                    raise NameError(f"Variable '{argName}' not found")
                executedLine = bodyLine.replace(func['params']['paramName'], argName)
            else:
                executedLine = bodyLine
            
            if executedLine.startswith('its giving'):
                returnValue = self.executeReturn(executedLine)
            elif executedLine.startswith('yap'):
                self.executeYap(executedLine)
                
        return returnValue if returnValue is not None else None
                
    def executeReturn(self, line: str) -> Any:
        match = re.match(r'its\s+giving\s*\((.*)\)', line)
        if not match:
            raise SyntaxError(f"Invalid return statement: {line}")
                
        expr = match.group(1).strip()
        
        if expr in self.variables:
            return self.variables[expr]
        elif expr.startswith('"') and expr.endswith('"'):
            return expr.strip('"')
        else:
            try:
                return self.evaluateMathExpression(expr)
            except:
                return expr

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