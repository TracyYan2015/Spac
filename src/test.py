import wx, wx.grid
import wx.lib.newevent
from Checker  import Checker
from Checker  import state
from os import popen
import os
import io


class Node:
    def __init__(self):
        self.fore = []
        self.next = []
        self.AP = {}

class ProbOfNode:
    def __init__(self): 
        self.nodeNo = 0
        self.prob = 0


class Test(wx.Frame):

    def PrintInConsole(self, msg):
        self.consoleTxt.AppendText('\n\n\n')
        self.consoleTxt.AppendText(msg)

    def AsyncPrint(self, event):
        self.PrintInConsole(event.output)

    def __init__(self):

        #hejia flag to show that all arguments are ready
        self.table_ok = False
        self.ltl_ok = False
        self.arg_ok = False

        wx.Frame.__init__(self, None, -1,
                                        "Spac",size = (800,500),
                                        style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        #hejia Add a panel to control background color
        # self.panel = wx.Panel(self, wx.ID_ANY)
        # self.panel.SetBackgroundColour('#FFFFFF')
        # self.panel.SetSize((800,500))
        # self.panel.SetSizer(self.Sizer)

        #hejia Add a top Sizer
        self.Sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SubSizer_L = wx.BoxSizer(wx.VERTICAL)


        self.Sizer.Add(self.SubSizer_L, 4, wx.EXPAND)

        #hejia table box
        self.nodes_tab_box = wx.BoxSizer(wx.VERTICAL)
        #hejia table tab
        topLbl = wx.StaticText(self,-1, " 1. Input number of nodes", size=(300,30))

        #hejia table number - adding number of them
        self.numTxt = wx.TextCtrl(self,-1,value='',size=(300, 30))

        #hejia table button box
        self.nodes_tab_btn_box = wx.BoxSizer(wx.HORIZONTAL)
        #hejia table buttons
        self.numButton = wx.Button(self,-1,label='Change Number',size=(150, 30))
        self.numButton.Bind(wx.EVT_BUTTON, self.OnNumButtonClick)
        self.numButton.Enable(False)
        self.numTxt.Bind(wx.EVT_TEXT,self.OnEnter)
        tableButton = wx.Button(self, label="Submit Table", size=(150, 30))
        tableButton.Bind(wx.EVT_BUTTON, self.OnTableClick)

        self.nodes_tab_box.Add(topLbl, 0, wx.EXPAND)
        self.nodes_tab_box.Add(self.numTxt, 0, wx.EXPAND)

        self.nodes_tab_btn_box.Add(self.numButton, 0, wx.EXPAND)
        self.nodes_tab_btn_box.Add(tableButton, 0, wx.EXPAND)

        self.SubSizer_L.Add(self.nodes_tab_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                           border=10 )
        self.SubSizer_L.Add(self.nodes_tab_btn_box,
                                           flag  =  wx.EXPAND  | wx.LEFT | wx.RIGHT ,
                                            border = 10)

        #hejia Add a blank margin
        self.SubSizer_L.Add((-1, 20))

        #enter LTl formula
        #hejia LTL box
        self.ltl_box = wx.BoxSizer(wx.VERTICAL)
        #hejia LTL elements
        LTLLbl = wx.StaticText(self,-1, "2. Enter the LTL formula", size=(300,30))

        self.LTLtxt = wx.TextCtrl(self,-1,value='',size=(300,30))

        #hejia button box
        self.ltl_btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.LTLButton = wx.Button(self,-1,label='Submit Property',size=(150,30))
        self.LTLButton.Bind(wx.EVT_BUTTON, self.OnLTLButtonClick)
    
        self.ltl_box.Add(LTLLbl, 0, wx.EXPAND)
        self.ltl_box.Add(self.LTLtxt, 0, wx.EXPAND)
        self.ltl_btn_box.Add(self.LTLButton, 0, wx.RIGHT | wx.ALIGN_RIGHT)

        self.SubSizer_L.Add(self.ltl_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT,
                                           border = 10)
        self.SubSizer_L.Add(self.ltl_btn_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT,
                                           border = 10)

        #hejia Add a blank margin
        self.SubSizer_L.Add((-1, 20))

        #Lynn checker input  @2015/6/22
        #hejia add arg table
        self.arg_box = wx.BoxSizer(wx.VERTICAL)
        #hejia arg elements
        chkLb = wx.StaticText(self,-1, " 3. Please enter a, b, c, d, k, p, op and check type, separated by '-' ")

        self.chktxt = wx.TextCtrl(self,-1,value='',size=(300,30))
        self.chktxt.AppendText('1-1-0.9-0.02-30-0.9->-0')

        self.arg_btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.chkButton = wx.Button(self,-1,label='Submit arguments', size=(150,30))
        self.chkButton.Bind(wx.EVT_BUTTON, self.OnchkButtonClick)
        self.check_btn = wx.Button(self, wx.ID_ANY, label='Start verifying', size=(150, 30) )
        self.check_btn.Bind(wx.EVT_BUTTON, self.StartVerify)

        self.arg_box.Add(chkLb, 0, wx.EXPAND)
        self.arg_box.Add(self.chktxt, 0, wx.EXPAND)
        self.arg_btn_box.Add(self.chkButton, 0, wx.RIGHT | wx.ALIGN_RIGHT)
        self.arg_btn_box.Add(self.check_btn, 0, wx.RIGHT | wx.ALIGN_RIGHT)

        self.SubSizer_L.Add(self.arg_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT,
                                           border = 10)
        self.SubSizer_L.Add(self.arg_btn_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT,
                                           border = 10)

        #hejia Add a blank margin
        self.SubSizer_L.Add((-1, 20))

        #hejia console box
        help_info_k =\
'''How to start:

1. If your DTMC has more or less nodes, change table's size in the top text area.
   Then click 'Change Number'.

2. Then you can input probability of transitions in the right table.

3. Click 'Submit Table' to finish model editing.
   ( Filling cell '(x, y)' with 0.1 means that state x may transits to state y by probability 10%.
   AP means 'atomic proposition', separating APs by ','.)
   ( Caution: The sum of a row must equal to 1.)

3. You can input property to verify in the second text area.
   The formula should be expressed by LTL.
   Click 'Submit Property' to finish.

4. Some arguments should be provided in the third text area. They are:
    a: Alpha parameter of beta distribution, which is used to define prior distribution. ( a > 0 )
    b: Beta parameter of beta distribution, which is used to define prior distribution. ( b > 0 )
    c: Confidence of the result. ( 0 <= c < 1 ).
    d: Approximate parameter. ( 0 < d < 1 ).
    k: Length of path to sample. ( k > 0 )
    p: Probability threshold of PBLTL. ( 0 <= p <= 1)
    op: Probability operator of PBLTL. ( op must be in { <, =, > } )
    check type: If this value=0, result is either "The model satisfies the LTL." or not.
    If this value=1, this tool will tell you the probability of the model satisfies the property.

5. At last, click 'Submit arguments' and then 'Start verifying' to start checking process.
'''

        self.console_box = wx.BoxSizer(wx.VERTICAL)
        self.consoleLb = wx.StaticText(self, wx.ID_ANY, 'Console')

        self.consoleTxt = wx.TextCtrl(self,-1,style=wx.TE_MULTILINE | wx.TE_READONLY, value='', size=(300,120))
        self.consoleTxt.Value = help_info_k

        self.console_box.Add(self.consoleLb, 0, wx.EXPAND)
        self.console_box.Add(self.consoleTxt, 0, wx.EXPAND)

        self.SubSizer_L.Add(self.console_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT,
                                           border = 10)


        #hejia ________________________________________add right box here
        self.SubSizer_R = wx.BoxSizer(wx.VERTICAL)

        #hejia change grids' position
        #hejia grid box
        self.grid_box = wx.BoxSizer(wx.VERTICAL)
        self.foreNum = 2
        self.nowNum = 2
        self.grid = wx.grid.Grid(self, size = (460, 460))
        self.grid.CreateGrid(3,2)
        for row in range(3):
            self.grid.SetColLabelValue(row, str(row+1))
            for col in range(2):
                self.grid.SetCellValue(row, col, "0")
        self.grid.SetRowLabelValue(2, "AP")

        #number of nodes
        self.num = 0
        #TODO(kk) add nodeList
        self.nodeList = []

        #hejia Add a blank margin
        self.grid_box.Add((-1, 20))
        self.grid_box.Add(self.grid, 1, wx.EXPAND)

        self.SubSizer_R.Add(self.grid_box,
                                           flag = wx.EXPAND | wx.LEFT | wx.RIGHT,
                                           border = 10)
        self.Sizer.Add(self.SubSizer_R, 6, wx.EXPAND)


        #PATCH hejia add Events @2015/7/30
        #If Check finished, it would add a result variable.
        self.FinishEventClass, self.FINISH_EVENT_ID =  wx.lib.newevent.NewEvent()
        self.Bind(self.FINISH_EVENT_ID, self.AsyncPrint)


    #Lynn creates @2015/6/22 
    def OnchkButtonClick(self, event):
        argu=self.chktxt.GetValue()
        arguTb=argu.split('-')
        #check number of arguments
        if len(arguTb)!=8:
            retCode = wx.MessageBox("Not enough arguments.Please enter again!", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return  
        #check abk
        if (eval(arguTb[0])<=0)  or  (eval(arguTb[1])<=0)  or  (eval(arguTb[4])<=0):
            retCode = wx.MessageBox("abk should be positive, enter again.", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return  
        #check c
        if (eval(arguTb[2])>1)  or  (eval(arguTb[2])<0) :
            retCode = wx.MessageBox("c should be [0,1], enter again.", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return  
        #check d
        if (eval(arguTb[3])>1)  or  (eval(arguTb[3])<0) :
            retCode = wx.MessageBox("d should be [0,1], enter again.", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return  
        #check p
        if (eval(arguTb[5])>1)  or  (eval(arguTb[5])<0) :
            retCode = wx.MessageBox("p should be [0,1], enter again.", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return  
        #check op
        if (arguTb[6]!='<')  and  (arguTb[6]!='>')  and (arguTb[6]!='=')  and (arguTb[6]!='<=')  and (arguTb[6]!='>='):
            retCode = wx.MessageBox("op should be <or>or=or<=or>=, enter again.", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return  
        #check check_type
        if (eval(arguTb[7])!=1)  and  (eval(arguTb[7])!=0):
            retCode = wx.MessageBox("check type should be 0 or 1, enter again.", "Arguments check",wx.OK | wx.ICON_QUESTION)
            return
        #if all the check passed, then it's legal
        self.arguTb=argu.split('-')

        #hejia log
        self.PrintInConsole('Arguments are accepted.')
        self.arg_ok  = True;

        return

    def StartVerify(self, event):
        s = self
        if s.table_ok and s.ltl_ok and s.arg_ok :
            if len( s.nodeList )<0 :
                return
            self.pts = s.__TranslateModel()
            #TODO(kk) need to add input of a, b, c, d, k, p, op
            #Lynn creates @2015/6/22
            self.a = eval(self.arguTb[0])
            self.b = eval(self.arguTb[1])
            self.c = eval(self.arguTb[2])
            self.d = eval(self.arguTb[3])
            self.k = eval(self.arguTb[4])
            self.p = eval(self.arguTb[5])
            self.op = self.arguTb[6]
            self.check_type = eval(self.arguTb[7])
            checker = Checker( self.pts, self.ltl,
                               self.a, self.b, self.c, self.d,
                               self.k, self.p,
                               self.op, self.check_type,
                               self, self.FinishEventClass)

            #hejia log
            self.PrintInConsole('Prepare to verify...')
            #hejia start a thread to verify
            checker.start()
            return

        if not s.table_ok:
            #hejia log
            self.PrintInConsole('Model is not constructed, please check settings of table.')
        if not s.ltl_ok:
            #hejia log
            self.PrintInConsole(' AST of LTL is not constructed, please check settings of LTL.')
        if not s.arg_ok:
            #hejia log
            self.PrintInConsole('Arguments are not accepted, please check settings of arguments.')
        return

    #Trans model into data structure that can be verified by Checker
    def __TranslateModel(self):

        pts = list()
        id=1

        for node in self.nodeList:
            pre = []
            post = []

            for prenode in node.fore:
                pre.append([prenode.nodeNo+1, prenode.prob])
            for postnode in node.next:
                post.append([postnode.nodeNo+1, postnode.prob])

            AP = set(node.AP.keys())
            AP.add('true')

            s = state(id, pre, post, AP)
            pts.append(s)
            id += 1

        #The first element of ptr is the number of nodes.
        pts.insert(0, len(pts))
        return pts

    #Use Lynn's compiler to get an AST.
    def __TranslateLTL(self):
        s = self
        try:
            #TODO hj need try, check LTL content, get LTL
            file = popen( "echo '"+s.LTLtxt.GetValue()+"' | ./LTLcompiler_linux" )
            ltl_str = file.readline()
            ltl = ltl_str.split(' ')
            if  ltl.count('error') > 0 :
                return False, None
        except:
            return False, None
        return True, ltl

    def OnLTLButtonClick(self, event):
        s = self
        result, self.ltl = s.__TranslateLTL()
        if result :
            #hejia log
            self.PrintInConsole('The AST of LTL is constructed.')
            s.ltl_ok = True
        else:
            #hejia log
            self.PrintInConsole('''Errors occur when AST is constructing.
                                               This may be caused by  no .Net Framework installed
                                               or failing to compile LTL.''')

    def OnTableClick(self, event):
        #hejia refresh the nodeList
        self.nodeList = []
        #check wethere every node's output is 1
        for x in range(0,self.nowNum):
            sum = 0
            for y in range(0,self.nowNum):
                if eval(self.grid.GetCellValue(x,y))<0 :
                    retCode = wx.MessageBox("Probability is negative. Please enter again!", "probability check",wx.OK | wx.ICON_QUESTION)
                    return                  
                sum+=eval(self.grid.GetCellValue(x,y))
            if sum!=1 :
                retCode = wx.MessageBox("The sum is not 1. Please enter again!", "probability check",wx.OK | wx.ICON_QUESTION)
                return
        #this i is the node number
        for i in range(0,self.nowNum):
            anode = Node()
            #nodeTable.append(anode)
            #serach for prior
            for j in range(0,self.nowNum):
                value = self.grid.GetCellValue(j,i)
                #value!="0" means it is anode's prior
                if value!="0" :
                    aprob = ProbOfNode()
                    aprob.nodeNo = j
                    aprob.prob = eval(value)
                    anode.fore.append(aprob)
                    aprob = ProbOfNode()
                APvalue = self.grid.GetCellValue(self.nowNum,i)
                APtable = APvalue.split(',')
                for item in APtable:
                    anode.AP[item] = i
            #search for the next one
            for j in range(0,self.nowNum):
                value = self.grid.GetCellValue(i,j)
                if value!="0" :
                    aprob = ProbOfNode()
                    aprob.nodeNo = j
                    aprob.prob = eval(value)
                    anode.next.append(aprob)
                    aprob = ProbOfNode()                  
            self.nodeList.append(anode)

        #hejia log
        self.PrintInConsole('Table is constructed.')
        self.table_ok = True
        
    def OnNumButtonClick(self, event):
        self.nowNum = eval(self.numTxt.GetValue())
        num = eval(self.numTxt.GetValue())-self.foreNum
        if num==0 :
            return
        if num>0 :
            self.grid.AppendCols(num)
            self.grid.AppendRows(num)
            for row in range(self.nowNum+1):
                self.grid.SetColLabelValue(row, str(row+1))
                for col in range(self.nowNum):
                    self.grid.SetRowLabelValue(col, str(col+1))
                    self.grid.SetCellValue(row, col, "0")
            self.grid.SetRowLabelValue(self.nowNum, "AP")
            self.foreNum=eval(self.numTxt.GetValue())
            self.grid.Refresh() 
        if num<0 :
            num = -num
            self.grid.DeleteRows(0,num)
            self.grid.DeleteCols(0,num)
            for row in range(self.nowNum+1):
                self.grid.SetColLabelValue(row, str(row+1))
                for col in range(self.nowNum):
                    self.grid.SetRowLabelValue(col, str(col+1))
                    self.grid.SetCellValue(row, col, "0")
            self.grid.SetRowLabelValue(self.nowNum, "AP")
            self.foreNum=eval(self.numTxt.GetValue())
            self.grid.Refresh()

            #hejia  log
            self.PrintInConsole('The number of state is constructed. Edit the model in the right table.')

    def OnEnter(self,event):            
        try:
            z = False
            z = type(eval(self.numTxt.GetValue())) == int and ((eval(self.numTxt.GetValue()))>0)
        except:
            pass
        if z:
            self.numButton.Enable(True)    
        else:
            self.numButton.Enable(False)


app = wx.PySimpleApp()
app.TopWindow = Test()
app.TopWindow.Show()
app.MainLoop()

