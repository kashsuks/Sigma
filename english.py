import re
import sys

def englishInterpreter(code, filename=""):
    variables = {}
    functions = {}
    importedModules = {}

    def write(value):
        print(value)

    def callFunction(funcName, args):
        if funcName not in functions:
            raise NameError(f"Function '{funcName}' not defined")

        funcParams, funcBody = functions[funcName]

        if len(args) != len(funcParams):
            raise TypeError(f"Function '{funcName}' expects {len(funcParams)} arguments, but {len(args)} were given")

        localVars = variables.copy()
        for i, param in enumerate(funcParams):
            paramType, paramName = param.split()
            try:
                if paramType == "integer":
                    localVars[paramName] = int(args[i])
                elif paramType == "float":
                    localVars[paramName] = float(args[i])
                elif paramType == "string":
                    localVars[paramName] = str(args[i])
                else:
                    localVars[paramName] = args[i]
            except ValueError:
                raise TypeError(f"Argument for '{paramName}' must be of type {paramType}")

        executeBlock(funcBody, localVars)

    def executeBlock(block, currentVars):
        for line in block:
            executeLine(line, currentVars)

    def executeLine(line, currentVars):
        line = line.strip()
        if not line or line.startswith("//"):
            return

        if line.startswith("integer"):
            if not line.endswith(";"):
                raise SyntaxError(f"Missing semicolon at the end of line: {line}")
            parts = line[:-1].split("=")
            varName = parts[0].split()[1].strip()
            try:
                currentVars[varName] = int(parts[1].strip())
            except ValueError:
                raise ValueError(f"Cannot assign non-integer value to integer variable {varName}")
        elif line.startswith("float"):
            if not line.endswith(";"):
                raise SyntaxError(f"Missing semicolon at the end of line: {line}")
            parts = line[:-1].split("=")
            varName = parts[0].split()[1].strip()
            try:
                currentVars[varName] = float(parts[1].strip())
            except ValueError:
                raise ValueError(f"Cannot assign non-float value to float variable {varName}")
        elif line.startswith("string"):
            if not line.endswith(";"):
                raise SyntaxError(f"Missing semicolon at the end of line: {line}")
            parts = line[:-1].split("=")
            varName = parts[0].split()[1].strip()
            currentVars[varName] = parts[1].strip().strip('"')
        elif line.startswith("write"):
            if not line.endswith(";"):
                raise SyntaxError(f"Missing semicolon at the end of line: {line}")
            value = line[6:-1].strip()
            if value in currentVars:
                write(currentVars[value])
            else:
                try:
                    write(int(value))
                except ValueError:
                    try:
                        write(float(value))
                    except ValueError:
                        write(value.strip('"'))
        elif line.startswith("call"):
            if not line.endswith(";"):
                raise SyntaxError(f"Missing semicolon at the end of line: {line}")
            parts = line[5:].strip().split("(")
            funcName = parts[0].strip()
            argsStr = parts[1][:-1].strip()
            args = []
            if argsStr:
                for arg in argsStr.split(','):
                    arg = arg.strip()
                    if arg in currentVars:
                        args.append(currentVars[arg])
                    else:
                        try:
                            args.append(int(arg))
                        except ValueError:
                            try:
                                args.append(float(arg))
                            except ValueError:
                                args.append(arg.strip('"'))
            callFunction(funcName, args)
        elif line.strip():
            raise SyntaxError(f"Invalid statement or missing semicolon: {line}")

    code = code.replace("BEGIN", "").replace("END", "").strip()
    code = re.sub(r'\n\s*', ';', code)

    if "take * from english" in code:
        importedModules["english"] = {"write": write}
        code = code.replace("take * from english", "")

    functionMatch = re.findall(r"function\s+(\w+)\((.*?)\)\s*{(.*?)}", code, re.DOTALL)
    for match in functionMatch:
        funcName, paramsStr, funcBody = match
        params = [p.strip() for p in paramsStr.split(",")] if paramsStr else []
        params = [p.replace(",", "") for p in params]
        functions[funcName] = (params, funcBody.strip().split(";"))

    code = re.sub(r"function\s+\w+\((.*?)\)\s*{(.*?)}", "", code, flags=re.DOTALL).strip()
    executeBlock(code.split(";"), variables)

def runEnglishFile(filename):
    if not filename.endswith(".en"):
        raise ValueError("Filename must end with .en")
    try:
        with open(filename, "r") as f:
            code = f.read()
            englishInterpreter(code, filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error in {filename}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python english.py <filename.en>")
        sys.exit(1)
    filename = sys.argv[1]
    runEnglishFile(filename)