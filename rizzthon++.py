import re
import sys

def rizzInterpreter(code, filename=""):
    lines = code.strip().split(";")
    variables = {}
    functions = {}
    importedModules = {}

    def yeet(value):
        print(value)

    def callFunction(funcName, args):
        if funcName not in functions:
            raise NameError(f"Function '{funcName}' not defined")

        funcParams, funcBody = functions[funcName]

        if len(args) != len(funcParams):
            raise TypeError(f"Function '{funcName}' expects {len(funcParams)} arguments, but {len(args)} were given")

        localVars = variables.copy()
        for i, param in enumerate(funcParams):
            paramType, paramName = param.split(":")
            try:
                if paramType == "int":
                    localVars[paramName] = int(args[i])
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

        if line.startswith("int"):
            parts = line.split("=")
            varName = parts[0].split()[1].strip()
            try:
                currentVars[varName] = int(parts[1].strip())
            except ValueError:
                raise ValueError(f"Cannot assign non-integer value to int variable {varName}")

        elif line.startswith("yeet"):
            value = line[5:-1].strip()
            if value in currentVars:
                yeet(currentVars[value])
            else:
                try:
                    yeet(int(value))
                except ValueError:
                    try:
                        yeet(float(value))
                    except ValueError:
                        yeet(value.strip('"'))
        elif line.startswith("call"):
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

    code = code.replace("BEGIN", "").replace("PERIOD", "").strip()

    if "rob * from rizz" in code:
        importedModules["rizz"] = {"yeet": yeet}
        code = code.replace("rob * from rizz", "")

    functionMatch = re.findall(r"tweak\s+(\w+)\((.*?)\)\s*{(.*?)}", code, re.DOTALL)
    for match in functionMatch:
        funcName, paramsStr, funcBody = match
        params = [p.strip() for p in paramsStr.split(",")] if paramsStr else []
        body = [b.strip() for b in funcBody.strip().split(";")]
        functions[funcName] = (params, body)

    remainingCode = re.sub(r"tweak\s+(\w+)\((.*?)\)\s*{(.*?)}", "", code, flags=re.DOTALL).strip()

    executeBlock(remainingCode.split(";"), variables)

def runRizzFile(filename):
    if not filename.endswith(".rizz"):
        raise ValueError("Filename must end with .rizz")
    try:
        with open(filename, "r") as f:
            code = f.read()
            rizzInterpreter(code, filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error in {filename}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rizzthon++.py <filename.rizz>")
        sys.exit(1)
    filename = sys.argv[1]
    runRizzFile(filename)