#!/usr/bin/python
import explores.ModulesFile as ModulesFile
model = ModulesFile.GYNCTMCModel()
model.prepareCommands()

# d, count, m, i, a, o


for _,c in md.commands.items():
    c.vs = vs
    c.cs = model.constants
    if c.evalGuard():
        print c.name

