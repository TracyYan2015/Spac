# -*- coding:utf-8 -*-
import ModulesFile
import logging
logging.basicConfig(level=logging.DEBUG)
from collections import OrderedDict
import copy

# class represents a DTMC/CTMC module in PRISM


class Module(object):
    # name: module name
    def __init__(self, name):
        self.name = name
        # TODO change to commName and comms implemention because commands may
        # have same name
        self.commands = OrderedDict()
        self.variables = OrderedDict()
        self.constants = dict()
        self.modulesFile = None

    def addVariable(self, variable):
        self.variables[variable.name] = variable
        variable.module = self

    def removeVariable(self, varname):
        if not self.variables and varname not in self.variables.keys():
            return
        self.variables.pop(varname)

    def addCommand(self, command):
        self.commands[command.name] = command
        command.module = self

    def addConstant(self, name, value):
        self.constants[name] = value

    def getConstant(self, name):
        if name in self.constants:
            return self.constants[name]
        return None

    # exist for now in the case of experiment
    def setConstant(self, name, value):
        if name in self.constants:
            v = self.constants[name]
            self.constants[name] = value
        return v

    def getVariable(self, name):
        if name in self.variables:
            return self.variables[name]
        return None


class CommandKind:
    FAILURE, REPAIR, NONE = range(3)


class Command(object):
    # name: name of the command
    # about guard and action in Command:
        # they all take two dictionaries vs, cs(set of variables and constants)
        # as its parameter
    # module: Module instance which the command get attached to
    # kind: indicate the command is a failure/repair transition
    # according to the definition in p52-nakayama(1).pdf
    # is an instance of CommandKind
    # prob: represents probability/rate
    def __init__(
            self,
            name,
            guard,
            action,
            module,
            prob,
            kind=None,
            biasingRate=None):
        self.name = name
        self.guard = guard
        self.action = action
        self.prob = prob
        self.module = module
        self.kind = kind
        # biasing rate(probability of DTMC actually)
        # by failure biasing methods, such as SFB, BFB, ...
        # failure biasing doesn't change rate, it only changes
        # probability of the embedded DTMC
        self.biasingRate = biasingRate

    def evalGuard(self):
        if 'cs' in dir(self) and 'vs' in dir(self):
            return self.guard(self.vs, self.cs)
        else:
            logging.info('vs,cs not exist in Module %s' % self.module.name)

    def execAction(self):
        if 'vs' in dir(self) and 'cs' in dir(self):
            self.action(self.vs, self.cs)
        else:
            logging.info('vs,cs not exist in Module %s' % self.module.name)

    def __str__(self):
        return 'comm %s of module %s' % (self.name, self.module.name)


class TypeError(object):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "TypeError: %s" % self.message


class Variable(object):
    def __init__(
            self,
            name='',
            initVal=None,
            valRange=None,
            valType=None,
            bounded=True):
        self.name = name
        self.initVal = initVal
        self.bounded = bounded
        self.valRange = valRange
        self.valType = valType
        self.value = initVal

    # check if value is within the domain
    # (bounded or unbounded) of the variable
    def validate(self, value):
        if self.bounded:
            return value in self.valRange
        else:
            return isinstance(value, self.valType)

    def __cmp__(self, v):
        if isinstance(v, Variable) and self.valType == v.valType:
            return self.value.__cmp__(v.value)
        elif isinstance(v, self.valType):
            return self.value.__cmp__(v)

    def __str__(self):
        return '(%s = %s)' % (self.name, self.getValue())

    def setValue(self, v):
        if isinstance(v, self.valType):
            self.value = v
        elif isinstance(v, Variable) and self.valType == v.valType:
            self.value = v.value

    def getValue(self):
        return self.value

    # return list of Variable instance with all possible values
    def allVarsList(self):
        if not self.bounded:
            return TypeError("Variable is not bounded")

        l = list()
        for val in self.valRange:
            cp = copy.copy(self)
            cp.value = val
            l.append(cp)
        return l

    def __iadd__(self, other):
        if isinstance(other, Variable) and self.valType == other.valType:
            self.value += other.value
        elif isinstance(other, self.valType):
            self.value += other
        return self


# 1. AT697F CPU处理模块
# const double fail_d=1/(10*365*24*3600);
# const double tran_d=1/(12*3600);
# const double tran_r2=1/35;
# const double tau=1/600;
# const MAX_COUNT = 2;
# module AT697F
#     d:[0..2]init 2;
#     count:[0..MAX_COUNT+1] init 0;
#     [ ]d>0->fail_d:(d'=0);
#     [ ]d=2->tran_d:(d'=1);
#     [d_reboot] d=1->tran_r2:(d'=2);
#     [timeout]comb->tau:(count'=0);
#     [timeout]!comb->tau:(count'=min(count+1，MAX_COUNT+1));
# endmodule
def AT697F():
    AT697F = Module('AT697F')
    # add constants
    AT697F.addConstant('fail_d', 1.0 / (10 * 365 * 24 * 3600))
    AT697F.addConstant('tran_d', 1.0 / (12 * 3600))
    AT697F.addConstant('tran_r2', 1.0 / 35)
    AT697F.addConstant('normal_d', 1)
    AT697F.addConstant('tau', 1.0 / 600)
    AT697F.addConstant('MAX_COUNT', 2)
    # add variables
    var1 = Variable('d', 2, range(3), int, True)
    var2 = Variable(
        'count',
        0,
        range(
            AT697F.constants['MAX_COUNT'] +
            2),
        int,
        True)
    AT697F.addVariable(var1)
    AT697F.addVariable(var2)

    # vs: all variables in modulesFile
    # cs: all constants in modulesFile
    def up(vs, xs):
        i = vs['i']
        o = vs['o']
        a = vs['a']
        m = vs['m']
        d = vs['d']
        return d == 2 and m == 2 and i == 1 and o == 1 and a == 1

    def dangerOrDown(vs, cs):
        return not up(vs, cs)

    # add commands
    # def __init__(self, name, guard, action, module, prob):
    comm1 = Command(
        'd_fail',
        lambda vs,
        cs: vs['d'] > 0,
        lambda vs,
        cs: vs['d'].setValue(0),
        AT697F,
        AT697F.getConstant('fail_d'))
    comm2 = Command(
        'd_tran',
        lambda vs,
        cs: vs['d'] == 2,
        lambda vs,
        cs: vs['d'].setValue(1),
        AT697F,
        AT697F.getConstant('tran_d'))
    comm3 = Command(
        'd_reboot',
        lambda vs,
        cs: vs['d'] == 1,
        lambda vs,
        cs: vs['d'].setValue(2),
        AT697F,
        AT697F.getConstant('tran_r2'))
    comm4 = Command(
        'timeout1',
        up,
        lambda vs,
        cs: vs['count'].setValue(0),
        AT697F,
        AT697F.getConstant('tau'))
    comm5 = Command('timeout2', dangerOrDown, lambda vs, cs: vs['count'].setValue(min(
        vs['count'].getValue() + 1, cs['MAX_COUNT'] + 1)), AT697F, AT697F.getConstant('tau'))
    comm6 = Command(
        'd_normal',
        lambda vs,
        cs: vs['d'] == 2,
        lambda vs,
        cs: vs['d'].setValue(2),
        AT697F,
        AT697F.getConstant('normal_d'))
    AT697F.addCommand(comm1)
    AT697F.addCommand(comm2)
    AT697F.addCommand(comm3)
    AT697F.addCommand(comm4)
    AT697F.addCommand(comm5)
    AT697F.addCommand(comm6)

    return AT697F

# const double fail_b=1/(5*365*24*3600);
# const double tran_b=1/(12*3600); // 3600
# const double tran_r1=1/35;
# module AX2000
# m:[0..2] init 2;
# []m>0->fail_b:(m'=0);
# []m=2->tran_b:(m'=1);
# [b_reboot] m=1->tran_r1:(m'=2);
# endmodule


def AX2000():
    module = Module('AX2000')
    # constants
    module.addConstant('fail_b', 1.0 / (5 * 365 * 24 * 3600))
    module.addConstant('tran_b', 1.0 / (1 * 3600))
    module.addConstant('tran_r1', 1.0 / 35)
    module.addConstant('normal_b', 1)
    # variable
    var1 = Variable('m', 2, range(3), int, True)
    module.addVariable(var1)
    # commands
    comm1 = Command(
        'm_fail',
        lambda vs,
        cs: vs['m'].getValue() > 0,
        lambda vs,
        cs: vs['m'].setValue(0),
        module,
        module.getConstant('fail_b'))
    comm2 = Command(
        'm_tran',
        lambda vs,
        cs: vs['m'] == 2,
        lambda vs,
        cs: vs['m'].setValue(1),
        module,
        module.getConstant('tran_b'))
    comm3 = Command(
        'b_reboot',
        lambda vs,
        cs: vs['m'] == 1,
        lambda vs,
        cs: vs['m'].setValue(2),
        module,
        module.getConstant('tran_r1'))
    comm4 = Command(
        'm_normal',
        lambda vs,
        cs: vs['m'] == 2,
        lambda vs,
        cs: vs['m'].setValue(2),
        module,
        module.getConstant('normal_b'))
    module.addCommand(comm1)
    module.addCommand(comm2)
    module.addCommand(comm3)
    module.addCommand(comm4)
    return module

# 3. AFS600 数据处理模块
# const double fail_a = 1/(5*365*24*3600);
# module AFS600
#     i : [0..1] init 1;
#     [] i=1 -> fail_a : (i'=0);
# endmodule


# constant value used for Balanced Model
failrate = 1.0/(31*24*3600)
repairrate = 1.0/(60)

def AFS600():
    module = Module('AFS600')
    module.addConstant('fail_i', failrate) # failure rate: once per month
    module.addConstant('repair_i', repairrate)
    var = Variable('i', 1, range(2), int, True)
    module.addVariable(var)
    comm = Command(
        'i_fail',
        lambda vs,
        cs: vs['i'] == 1 and (vs['a'] == 1 or vs['da'] == 1),
        lambda vs,
        cs: vs['i'].setValue(0),
        module,
        module.getConstant('fail_i'),
        CommandKind.FAILURE)
    comm_repair = Command(
        'i_repair',
        lambda vs,
        cs: vs['i'] == 0 and vs['di'] == 1 and (vs['a'] == 1 or vs['da'] == 1),
        lambda vs,
        cs: vs['i'].setValue(1),
        module,
        module.getConstant('repair_i'),
        CommandKind.REPAIR)
    module.addCommand(comm)
    module.addCommand(comm_repair)
    return module


def dAFS600():
    module = Module('dAFS600')
    module.addConstant('dfail_i', failrate) # once per month
    module.addConstant('drepair_i', repairrate)
    var = Variable('di', 1, range(2), int, True)
    module.addVariable(var)
    comm = Command(
        'di_failure',
        lambda vs,
        cs: vs['di'] == 1 and (vs['a'] == 1 or vs['da'] == 1),
        lambda vs,
        cs: vs['di'].setValue(0),
        module,
        module.getConstant('dfail_i'),
        CommandKind.FAILURE)
    comm_repair = Command(
        'di_repair',
        lambda vs,
        cs: vs['di'] == 0 and vs['i'] == 1 and (vs['a'] == 1 or vs['da'] == 1),
        lambda vs,
        cs: vs['di'].setValue(1),
        module,
        module.getConstant('drepair_i'),
        CommandKind.REPAIR)

    module.addCommand(comm)
    module.addCommand(comm_repair)
    return module

# 4. V5-FPGA 指令解析模块
# const double fail_c = 1/(5*365*24*3600);
# module V5-FPGA
#     o : [0..1] init 1;
#     [] o=1 & (d=2&a=1) -> fail_c : (o'=0);
# endmodule

def V5_FPGA():
    module = Module('V5-FPGA')
    module.addConstant('fail_c', 1.0 / (5 * 365 * 24 * 3600))
    module.addConstant('normal_c', 1)
    var = Variable('o', 1, range(2), int, True)
    module.addVariable(var)

    def guard(vs, cs):
        return vs['o'] == 1 and vs['d'] \
            == 2 and vs['a'] == 1
    comm = Command(
        'o_fail',
        guard,
        lambda vs,
        cs: vs['o'].setValue(0),
        module,
        module.getConstant('fail_c'))
    comm1 = Command(
        'o_normal',
        lambda vs,
        cs: vs['o'] == 1,
        lambda vs,
        cs: vs['o'].setValue(1),
        module,
        module.getConstant('normal_c'))
    module.addCommand(comm)
    module.addCommand(comm1)

    return module

# 5. AT7910 总线模块
# const double fail_e=
#     1/(5*365*24*3600);
# module AT7910
#     a : [0..1] init 1;
#     [] a=1 -> fail_e : (a'=0);
# endmodule

def AT7910():
    module = Module('AT7910')
    module.addConstant('fail_e', failrate) # once per month
    module.addConstant('repair_e', repairrate)
    var = Variable('a', 1, range(2), int, True)
    module.addVariable(var)
    # failure transition
    comm = Command(
        'a_fail',
        lambda vs,
        cs: vs['a'] == 1 and (
            vs['i'] == 1 or vs['di'] == 1),
        lambda vs,
        cs: vs['a'].setValue(0),
        module,
        module.getConstant('fail_e'),
        CommandKind.FAILURE)
    commrepair = Command(
        'a_repair',
        lambda vs,cs: vs['a'] == 0 and vs['da'] == 1 and (vs['i'] == 1 or vs['di'] == 1),
        lambda vs, cs: vs['a'].setValue(1),
        module,
        module.getConstant('repair_e'),
        CommandKind.REPAIR
    )
    module.addCommand(commrepair)
    module.addCommand(comm)

    return module


def dAT7910():
    module = Module('dAT7910')
    module.addConstant('dfail_e', failrate) # once per month
    module.addConstant('drepair_e', repairrate)
    var = Variable('da', 1, range(2), int, True)
    module.addVariable(var)
    # failure transition
    comm = Command(
        'da_fail',
        lambda vs,
        cs: vs['da'] == 1 and (
            vs['i'] == 1 or vs['di'] == 1),
        lambda vs,
        cs: vs['da'].setValue(0),
        module,
        module.getConstant('dfail_e'),
        CommandKind.FAILURE)
    commrepair = Command(
        'da_repair',
        lambda vs,
        cs: vs['da'] == 0 and vs['a'] == 1 and (
            vs['i'] == 1 or vs['di'] == 1),
        lambda vs,
        cs: vs['da'].setValue(1),
        module,
        module.getConstant(
            "drepair_e"),
            CommandKind.REPAIR)
    module.addCommand(comm)
    module.addCommand(commrepair)
    return module


# construct a toy module used for ToyModel
# which has a failure rate = 1e-5 and a repair rate = 2
def ToyModule():
    module = Module("ToyModule")
    module.addConstant("fail", 1e-6)
    module.addConstant("repair", 2.0)
    var = Variable('v', 1, range(2), int, True)
    module.addVariable(var)
    failurecomm = Command(
        'fail',
        lambda vs,
        cs: vs['v'] == 1,
        lambda vs,
        cs: vs['v'].setValue(0),
        module,
        module.getConstant("fail"),
        CommandKind.FAILURE)
    repaircomm = Command(
        'repair',
        lambda vs,
        cs: vs['v'] == 0,
        lambda vs,
        cs: vs['v'].setValue(0),
        module,
        module.getConstant('repair'),
        CommandKind.REPAIR)
    module.addCommand(failurecomm)
    module.addCommand(repaircomm)
    return module
