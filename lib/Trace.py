import sys

#first, get access to files.
TRACE_TOOLS_FOLDER = "/opt/trampoline/extra/trace-tools"
sys.path.append(TRACE_TOOLS_FOLDER)

try:
    import StaticInfo
    import TraceReader
    import TraceEvaluate
    import TraceExport
except ImportError:
    print("I can't find trace tools scripts")
    print("=> searched in '"+ TRACE_TOOLS_FOLDER +"'")
    print("Maybe the TRAMPOLINE_BASE_PATH is not correctly set in your .oil file")
    print("Correct it and run goil again.")
    sys.exit(1)

class TraceToolbox():
    def __init__(self, tpl_filename, trace_filename):
        self.si = StaticInfo.StaticInfo(tpl_filename)
        self.reader = TraceReader.TraceReaderFile(trace_filename)

        #evaluator => from raw events and Static info. Get events
        self.evaluator = TraceEvaluate.TraceEvaluate(self.si)

        #export    => font end (txt, gui)
        self.export = TraceExport.TraceExport()
        self.evaluator.setExport(self.export)