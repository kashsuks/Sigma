import re
import sys
from typing import Any, Dict, List, Union

class SigmaInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, dict] = {}
    
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
        # Replace variables with their values
        for varName, varValue in self.variables.items():
            if isinstance(varValue, (int, float)):
                expr = expr.replace(varName, str(varValue))
        
        # Handle basic operations
        if '+' in expr:
            parts = expr.split('+')
            return sum(float(part.strip()) for part in parts)
        elif '-' in expr:
            parts = expr.split('-')
            result = float(parts[0].strip())
            for part in parts[1:]:
                result -= float(part.strip())
            return result
        elif '*' in expr:
            parts = expr.split('*')
            result = 1
            for part in parts:
                result *= float(part.strip())
            return result
        elif '/' in expr:
            parts = expr.split('/')
            result = float(parts[0].strip())
            for part in parts[1:]:
                value = float(part.strip())
                if value == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= value
            return result
        else:
            return float(expr.strip())
    
    def tokenize(self, code: str) -> List[str]:
        # Remove comments
        code = re.sub(r'//.*', '', code)
        # Split into lines and remove empty lines
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        return lines

    def parseAndExecute(self, code: str) -> None:
        lines = self.tokenize(code)
        
        if lines[0] != "BEGIN" or lines[-1] != "PERIOD":
            raise SyntaxError("Code must start with BEGIN and end with PERIOD")
        
        # Remove BEGIN and PERIOD
        lines = lines[1:-1]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip imports for now
            if line.startswith('rob'):
                i += 1
                continue
                
            # Function definition
            if line.startswith('tweak'):
                funcDef = self.parseFunction(lines[i:])
                i += funcDef['linesConsumed']
                continue
                
            # Function call
            if line.startswith('call'):
                self.executeFunctionCall(line)
                
            # Variable declaration
            elif any(typeName in line for typeName in ['int', 'bool', 'str', 'float']):
                self.declareVariable(line)
                
            # Built-in function calls
            elif line.startswith('yap'):
                self.executeYap(line)
                
            i += 1

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

    def declareVariable(self, line: str) -> None:
        parts = line.split('=')
        if len(parts) != 2:
            raise SyntaxError(f"Invalid variable declaration: {line}")
            
        varDef = parts[0].strip()
        value = parts[1].strip()
        
        typeName, varName = varDef.split()
        varName = varName.strip()
        
        # Handle mathematical expressions in variable declarations
        if typeName in ['int', 'float']:
            try:
                evaluated_value = self.evaluateMathExpression(value)
                if typeName == 'int':
                    value = int(evaluated_value)
                else:
                    value = float(evaluated_value)
            except Exception as e:
                raise SyntaxError(f"Invalid mathematical expression: {value}")
        elif typeName == 'bool':
            value = value.lower() == 'true'
        elif typeName == 'str':
            value = value.strip('"')
            
        self.variables[varName] = value

    def executeYap(self, line: str) -> None:
        match = re.match(r'yap\((\w+)\)', line)
        if not match:
            raise SyntaxError(f"Invalid yap statement: {line}")
            
        varName = match.group(1)
        if varName not in self.variables:
            raise NameError(f"Variable '{varName}' not found")
            
        print(self.variables[varName])

    def executeFunctionCall(self, line: str) -> None:
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
        
        # Execute function body
        for bodyLine in func['body']:
            # Replace parameter with argument in the body
            executedLine = bodyLine.replace(func['paramName'], argName)
            
            if executedLine.startswith('yap'):
                self.executeYap(executedLine)

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