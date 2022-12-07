from time import strftime
import cv2
import kivy
import pyrebase
import numpy as np
import mediapipe as mp
import json
import math
from datetime import datetime
from datetime import date
from kivy.app import App
from kivymd.app import MDApp

from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, LinePlot, MeshLinePlot
from kivy.core.text import LabelBase

kivy.require('2.1.0')
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

myjsonfile=open('firebaseConfig.json','r')
firebaseC=myjsonfile.read()

firebaseConfig = json.loads(firebaseC)
print(firebaseConfig)

firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()
auth=firebase.auth()

class Sp(SpinnerOption):
    color = (49/255, 112/255, 167/255, 1)
    background_color= (190/255, 227/255, 234/255, 1)
    background_normal = " "
    spacing = Window.height/10

LabelBase.register(name="Righteous", fn_regular="Righteous-Regular.ttf")
Window.size=(375,750)

class KivyApp(App):

    def build(self):
        #welcome screen
        self.mainscreen = Image(size_hint=(1, 1), color=(253/255, 237/255, 221/255, 1), pos=(0,0))
        self.symbol=Image(source="symbol1.png" , allow_stretch=True, size_hint=(0.7,1.1),pos_hint={"center_x": .5, "center_y": .5}, opacity=0.4)
        self.appName = Label(text="StreBit", size_hint=(1, .5), pos_hint={"center_x": .5, "center_y": .7},
                               color=(60 / 255, 70 / 255, 94 / 255, 1), font_size="90sp", font_name="Righteous")
        self.welbutton = Button(text="Start", size_hint=(.4, .1), pos_hint={"center_x": .5, "center_y": .45},font_size="20sp",background_normal=" ",
                                color=(253 / 255, 237 / 255, 221 / 255, 1),background_color=(60 / 255, 70 / 255, 94 / 255, 1))
        self.welbutton.bind(on_press=self.welcometologin)
        self.capture = None
        #main page
        self.points=[]
        self.startbutton=Button(text="Tests",size_hint=(.8,.35), pos_hint={"center_x": .5, "center_y": .7}, font_size="30sp",
                           background_normal= " ", background_color=(253/255, 237/255, 221/255, 1), color=(60/255, 70/255, 94/255, 1))
        #self.mainlabel=Label(text="Flexibility Tests",size_hint=(1,.1), pos_hint={"center_x": .5, "center_y": .7}, color=(253/255, 237/255, 221/255, 1),font_size="20sp")
        self.startbutton.bind(on_press=self.menuscreen)
        self.resultspageB = Button(text="Results", size_hint=(.8, .35), pos_hint={"center_x": .5, "center_y": .3},font_size="30sp",background_normal=" ",
                                   background_color=(253 / 255, 237 / 255, 221 / 255, 1),color=(60 / 255, 70 / 255, 94 / 255, 1))
        self.resultspageB.bind(on_press=self.maintodata)
        #log in screen
        self.e=None
        self.logintitle= Label(text="Login",size_hint=(1,.1), pos_hint={"center_x": .5, "center_y": .75}, color=(253/255, 237/255, 221/255, 1),font_size="30sp")
        self.lemail=Label(text="Email:",size_hint=(1,.1), pos_hint={"center_x": .25, "center_y": .6}, color=(253/255, 237/255, 221/255, 1),font_size=Window.width*0.02)
        self.lpassword = Label(text="Password:", size_hint=(.5, .1), pos_hint={"center_x": .25, "center_y": .50},color=(253 / 255, 237 / 255, 221 / 255, 1),font_size=Window.width * 0.02)
        self.emailinput=TextInput(multiline=False,size_hint=(0.5,0.05), pos_hint={"center_x": .67, "center_y": .6} )
        self.passinput=TextInput(multiline=False,size_hint=(0.5,0.05), pos_hint={"center_x": .67, "center_y": .50} )
        self.authbutton = Button(text="Login", size_hint=(.2, .05), pos_hint={"center_x": .8, "center_y": .4},font_size=Window.width * 0.02,
                                  background_normal=" ", background_color=(253 / 255, 237 / 255, 221 / 255, 1),color=(60 / 255, 70 / 255, 94 / 255, 1))
        self.authbutton.bind(on_press=self.signin)
        self.lcreateaccount = Button(text="Create An Account", size_hint=(.2, .05), pos_hint={"center_x": .35, "center_y": .4},font_size=Window.width * 0.02, underline= True,
                                 background_normal=" ", color=(253 / 255, 237 / 255, 221 / 255, 1),background_color=(60 / 255, 70 / 255, 94 / 255, 1))
        self.lcreateaccount.bind(on_press=self.createanaccountscreen)
        self.logintowelB = Button(text="Back", color=(60 / 255, 70 / 255, 94 / 255, 1), background_normal=" ",background_color=(253 / 255, 237 / 255, 221 / 255, 1),
                                  size_hint=(.15, .05), pos_hint={"center_x": .15, "center_y": .9})
        self.logintowelB.bind(on_press=self.logintowelcome)
        self.lincorrect=Label(text="There is an empty field.", size_hint=(.7, .1), pos_hint={"center_x": .5, "center_y": .3},color=(1,0,0, 1),font_size=Window.width * 0.02)
        #create an account screen
        self.confpassword = Label(text="Confirm Password:", size_hint=(.5, .1), pos_hint={"center_x": .23, "center_y": .4},color=(253 / 255, 237 / 255, 221 / 255, 1), font_size=Window.width * 0.02)
        self.confpassinput = TextInput(multiline=False, size_hint=(0.5, 0.05), pos_hint={"center_x": .67, "center_y": .4})
        self.createaccountB = Button(text="Create", size_hint=(.15, .05), pos_hint={"center_x": .8, "center_y": .3},font_size=Window.width * 0.02,background_normal=" ",
                                     background_color=(253 / 255, 237 / 255, 221 / 255, 1),color=(60 / 255, 70 / 255, 94 / 255, 1))
        self.createaccountB.bind(on_press=self.createanaccount)
        self.createtologinB=Button(text="Login", color=(60/255, 70/255, 94/255, 1), background_normal= " ", background_color=(253/255, 237/255, 221/255, 1),
                               size_hint=(.15, .05), pos_hint= {"center_x": .15, "center_y": .9})
        self.createtologinB.bind(on_press=self.backtologin)
        #menu screen
        self.topstrip=Image(size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "center_y": .95}, color=(60/255, 70/255, 94/255, 1))
        self.snrbutton=Button(text="Stand & Reach", color=(1, 1, 1, 1), size_hint=( .4, .2), background_normal= " ",
                              background_color= (60/255, 70/255, 94/255, 1), pos_hint={"center_x": .25, "center_y": .75})
        self.snrbutton.bind(on_press=self.menutoSNRI)
        self.backbutton1=Button(text="Main", color=(60/255, 70/255, 94/255, 1), background_normal= " ", background_color=(253/255, 237/255, 221/255, 1),
                               size_hint=(.15, .05), pos_hint= {"center_x": .15, "center_y": .95})
        self.backbutton1.bind(on_press=self.backtomainscreen)
        self.morecoming=Button(text= "More Coming",color= (60/255, 70/255, 94/255, 1),background_normal= " ",
                            background_color=( 253/255, 237/255, 221/255, 1), size_hint=(.4, .2), pos_hint= {"center_x": .75, "center_y": .75}, disabled= True)
        #Stand and Reach Instruction Screen
        self.SNRItomenuB = Button(text="Menu", color=(1,1,1, 1), background_normal=" ",background_color=(60 / 255, 70 / 255, 94 / 255, 1),
                                  size_hint=(.15, .05), pos_hint={"center_x": .15, "center_y": .93})
        self.SNRItomenuB.bind(on_press=self.SNRItomenu)
        self.SNRItoCountB = Button(text="Start", color=(1, 1, 1, 1), size_hint=(.3, .07), background_normal=" ",background_color=(60 / 255, 70 / 255, 94 / 255, 1),
                                pos_hint={"center_x": .5, "center_y": .1})
        self.SNRItoCountB.bind(on_press=self.countdowntimer)
        self.SNRlabel = Label(text="Stand & Reach", size_hint=(1, .5), pos_hint={"center_x": .5, "center_y": .8},
                             color=(60 / 255, 70 / 255, 94 / 255, 1), font_size="40sp")
        self.SNRIwarning = Label(text='''Warning: Do not got pass your limit.
                                      \nGo to your most comfortable position
                                      \nand wait until your score is taken.''',
                                 size_hint=(1, .5), pos_hint={"center_x": .5, "center_y": .3},color=(1,0,0, 1), font_size="15sp", halign="center", line_height=0.7)
        self.SNRinstr = Label(text='''For this test, you will need to stand up
                                    \nstraight and bend over. 
                                    \nMake sure have your left shoulder, hip,
                                    \nand foot visible in the camera.  
                                    \nThe smaller the score, the more flexible you are.
                                    \nYou have 10 seconds to get ready.''',
                              size_hint=(.7, .5), pos_hint={"center_x": .5, "center_y": .6},
                              color=(60 / 255, 70 / 255, 94 / 255, 1), font_size="15sp", halign="center", line_height=0.7)
        #test screen
        self.webcam = Image(size_hint=(1, 0.8), pos_hint={"center_x": .5, "center_y": .5})
        self.snrprogress=ProgressBar(max=20, value=0, pos_hint={"center_x": .5, "center_y": .8}, size_hint=(0.8, 0.05))
        #result screen
        self.snrdoneresult = Label(text="Done", size_hint=(1, .4), pos_hint={"center_x": .5, "center_y": .6},color=(253 / 255, 237 / 255, 221 / 255, 1),
                                   font_size="50sp")
        self.snrback=Button(text="Main", color=(60/255, 70/255, 94/255, 1), background_normal= " ", background_color=(253/255, 237/255, 221/255, 1),
                               size_hint=(.17, .1), pos_hint= {"center_x": .32, "center_y": .35})
        self.snrback.bind(on_press=self.snrbacktomain)
        self.redobutton=Button(text="Redo", color=(60/255, 70/255, 94/255, 1), background_normal= " ", background_color=(253/255, 237/255, 221/255, 1),
                               size_hint=(.17, .1), pos_hint= {"center_x": .68, "center_y": .35})
        self.redobutton.bind(on_press=self.redotest)
        self.resultnum=0
        #timer screen
        self.countdownnum=10
        self.countdown=Label(text=str(self.countdownnum),size_hint=Window.size, pos_hint={"center_x": .5, "center_y": .5}, color=(1,1,1, 1),font_size=Window.width*0.3)
        #data page
        self.databacktomain = Button(text="Main", color=(60 / 255, 70 / 255, 94 / 255, 1), background_normal=" ", background_color=(253 / 255, 237 / 255, 221 / 255, 1),
                                  size_hint=(.15, .05), pos_hint={"center_x": .15, "center_y": .95})
        self.databacktomain.bind(on_press=self.datatomain)
        self.neweststrip = Image(size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "center_y": .80},
                              color=(11 / 255, 45 / 255, 100 / 255, 1))
        self.newscoreL = Label(text="", size_hint=(1,0.1),pos_hint={"center_x": .5, "center_y": .80}, color=(186/255, 204/255, 217/255, 1),
                               font_size=Window.width * 0.02)
        self.datadisplay = Spinner(text="Today", values=["0"],pos_hint={"center_x": .5, "center_y": .65},sync_height=True,size_hint=(1, 0.1) ,
                                   text_autoupdate=False,background_color=(11 / 255, 45 / 255, 100 / 255, 1),
                                  color=(11 / 255, 45 / 255, 100 / 255, 1), disabled=True, option_cls=Factory.get("Sp"))
        self.datastrip = Image(size_hint=(1, 0.1), pos_hint={"center_x": .5, "center_y": .65},color=(11 / 255, 45 / 255, 100 / 255, 1))
        self.todaydataB = Button(text="Today", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                size_hint=(.15, 0.05), pos_hint={"center_x": .1, "center_y": .65}, background_normal=" ")
        self.todaydataB.bind(on_press=self.todayDataInfo)
        self.weekdataB = Button(text="Week", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                size_hint=(.15, 0.05), pos_hint={"center_x": .3, "center_y": .65}, background_normal=" ")
        self.weekdataB.bind(on_press=self.weekDataInfo)
        self.monthdataB =  Button(text="Month", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                size_hint=(.15, 0.05), pos_hint={"center_x": .5, "center_y": .65}, background_normal=" ")
        self.monthdataB.bind(on_press=self.monthDataInfo)
        self.yeardataB = Button(text="Year", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                 size_hint=(.15, 0.05), pos_hint={"center_x": .7, "center_y": .65},background_normal=" ")
        self.yeardataB.bind(on_press=self.yearDataInfo)
        self.alldataB =  Button(text="All", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                size_hint=(.15, 0.05), pos_hint={"center_x": .9, "center_y": .65}, background_normal=" ")
        self.alldataB.bind(on_press=self.allDataInfo)
        self.graphB=Button(text="Graphs", color=(60 / 255, 70 / 255, 94 / 255, 1), background_normal=" ", background_color=(253 / 255, 237 / 255, 221 / 255, 1),
                                  size_hint=(.15, .05), pos_hint={"center_x": .85, "center_y": .95})
        self.graphB.bind(on_press=self.datatograph)
        self.datalist=[]
        self.todayTime=0
        self.weekday=0
        self.now=0
        self.weekdataset = []
        self.monthdataset = []
        self.yeardataset = []
        self.alldataset = []
        #Graph Page
        self.graphtodataB = Button(text="Data", color=(60 / 255, 70 / 255, 94 / 255, 1), background_normal=" ",background_color=(253 / 255, 237 / 255, 221 / 255, 1),
                                     size_hint=(.15, .05), pos_hint={"center_x": .15, "center_y": .95})
        self.graphtodataB.bind(on_press=self.graphtodata)
        self.weekgraphB = Button(text="Week", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                size_hint=(.15, 0.05), pos_hint={"center_x": .2, "center_y": .8}, background_normal=" ")
        self.weekgraphB.bind(on_press=self.weekGraph)
        self.monthgraphB = Button(text="Month", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                 size_hint=(.15, 0.05), pos_hint={"center_x": .4, "center_y": .8},background_normal=" ")
        self.monthgraphB.bind(on_press=self.monthGraph)
        self.yeargraphB = Button(text="Year", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                                size_hint=(.15, 0.05), pos_hint={"center_x": .6, "center_y": .8},background_normal=" ")
        self.yeargraphB.bind(on_press=self.yearGraph)
        self.allgraphB = Button(text="All", background_color=(186 / 255, 204 / 255, 217 / 255, 1),color=(11 / 255, 45 / 255, 100 / 255, 1),
                               size_hint=(.15, 0.05), pos_hint={"center_x": .8, "center_y": .8}, background_normal=" ")
        self.allgraphB.bind(on_press=self.allGraph)
        self.weekdatasetx = []
        self.monthdatasetx=[]
        self.yeardatasetx = []
        self.alldatasetx = []
        self.graph = Graph(size_hint=(.9, 0.6),pos_hint={"center_x": .5, "center_y": .4},xmin=0, xmax=10, ymin=0, ymax=1, background_color=(11 / 255, 45 / 255, 100 / 255, 1)
                           , ylabel="Score", y_ticks_major=0.1, border_color=(167/255, 170/255, 171/255, 1), draw_border=True,
                           tick_color=(1, 1, 1, 1),y_grid=True, x_ticks_major=1, x_grid=True, y_grid_label=True, opacity=0)
        self.plot = LinePlot(color=(190 / 255, 227 / 255, 234 / 255, 1),line_width=5)
        #Starting Elements
        self.layout=RelativeLayout()
        self.layout.add_widget(self.mainscreen)
        self.layout.add_widget(self.symbol)
        self.layout.add_widget(self.appName)
        self.layout.add_widget(self.welbutton)
        return self.layout

    def welcometologin(self, events):
        self.mainscreen.color=(60 / 255, 70 / 255, 94 / 255, 1)
        self.layout.remove_widget(self.symbol)
        self.layout.remove_widget(self.appName)
        self.layout.remove_widget(self.welbutton)
        self.layout.add_widget(self.logintitle)
        self.layout.add_widget(self.lemail)
        self.layout.add_widget(self.lpassword)
        self.layout.add_widget(self.emailinput)
        self.layout.add_widget(self.passinput)
        self.layout.add_widget(self.authbutton)
        self.layout.add_widget(self.lcreateaccount)
        self.layout.add_widget(self.logintowelB)

    def logintowelcome(self, events):
        self.mainscreen.color=color=(253/255, 237/255, 221/255, 1)
        self.layout.add_widget(self.symbol)
        self.layout.add_widget(self.appName)
        self.layout.add_widget(self.welbutton)
        self.layout.remove_widget(self.logintitle)
        self.layout.remove_widget(self.lemail)
        self.layout.remove_widget(self.lpassword)
        self.layout.remove_widget(self.emailinput)
        self.layout.remove_widget(self.passinput)
        self.layout.remove_widget(self.authbutton)
        self.layout.remove_widget(self.lcreateaccount)
        self.layout.remove_widget(self.logintowelB)

    #def switchscreen(self,event):
       # Clock.schedule_interval(self.callback, 10/33)
    def loginscreen(self, events):
        self.layout.remove_widget(self.mainlabel)
        self.layout.remove_widget(self.startbutton)
        self.layout.add_widget(self.logintitle)
        self.layout.add_widget(self.lemail)
        self.layout.add_widget(self.lpassword)
        self.layout.add_widget(self.emailinput)
        self.layout.add_widget(self.passinput)
        self.layout.add_widget(self.authbutton)
        self.layout.add_widget(self.lcreateaccount)
        #self.layout.add_widget(self.logintowelB)

    def signin(self,event):
        email=self.emailinput.text
        password=self.passinput.text
        if len(email)==0 or len(password)==0:
            self.layout.add_widget(self.lincorrect)
            Clock.schedule_once(self.removeincorrect,5)
        else:
            try:
                auth.sign_in_with_email_and_password(email, password)
                self.layout.remove_widget(self.authbutton)
                self.layout.remove_widget(self.lcreateaccount)
                self.layout.remove_widget(self.logintowelB)
                #print("sucess")
                self.e=email
                self.mainscreendisplay()
            except:
                self.emailinput.text=""
                self.passinput.text=""
                self.lincorrect.text="Invalid user or password. Try Again"
                self.layout.add_widget(self.lincorrect)
                Clock.schedule_once(self.removeincorrect, 5)

    def removeincorrect(self,*args):
        self.layout.remove_widget(self.lincorrect)

    def createanaccountscreen(self, events):
        self.layout.remove_widget(self.lcreateaccount)
        self.layout.remove_widget(self.authbutton)
        self.layout.remove_widget(self.logintowelB)
        self.layout.add_widget(self.confpassword)
        self.layout.add_widget(self.confpassinput)
        self.logintitle.text="Create An Account"
        self.layout.add_widget(self.createaccountB)
        self.layout.add_widget(self.createtologinB)

    def createanaccount(self,event):
        email = self.emailinput.text
        password = self.passinput.text
        confirmpass=self.confpassinput.text
        self.lincorrect.pos_hint = {"center_x": .5, "center_y": .2}
        if len(email) == 0 or len(password) == 0 or len(confirmpass)==0:
            self.lincorrect.text="There is an empty field."
            self.layout.add_widget(self.lincorrect)
            Clock.schedule_once(self.removeincorrect, 5)
        else:
            if len(password)<6:
                self.lincorrect.text = "Weak password."
                self.layout.add_widget(self.lincorrect)
                Clock.schedule_once(self.removeincorrect, 5)
            else:
                if password!=confirmpass:
                    self.lincorrect.text = "Password does not match."
                    self.layout.add_widget(self.lincorrect)
                    Clock.schedule_once(self.removeincorrect, 5)
                else:
                    try:
                        auth.create_user_with_email_and_password(email,password)
                        self.layout.remove_widget(self.confpassword)
                        self.layout.remove_widget(self.confpassinput)
                        self.layout.remove_widget(self.createaccountB)
                        self.layout.remove_widget(self.createtologinB)
                        self.e = email
                        self.mainscreendisplay()
                    except:
                        self.lincorrect.text = "Email already exist."
                        self.layout.add_widget(self.lincorrect)
                        Clock.schedule_once(self.removeincorrect, 5)
        self.emailinput.text = ""
        self.passinput.text = ""
        self.confpassinput.text=""

    def backtologin(self, events):
        self.layout.add_widget(self.lcreateaccount)
        self.layout.add_widget(self.authbutton)
        self.layout.remove_widget(self.confpassword)
        self.layout.remove_widget(self.confpassinput)
        self.layout.add_widget(self.logintowelB)
        self.logintitle.text = "Login"
        self.layout.remove_widget(self.createaccountB)
        self.layout.remove_widget(self.createtologinB)

    def mainscreendisplay(self,*args):
        #self.layout.add_widget(self.mainlabel)
        self.layout.add_widget(self.startbutton)
        self.layout.add_widget(self.resultspageB)
        self.layout.remove_widget(self.logintitle)
        self.layout.remove_widget(self.lemail)
        self.layout.remove_widget(self.lpassword)
        self.layout.remove_widget(self.emailinput)
        self.layout.remove_widget(self.passinput)

    def menuscreen(self, event):
        self.mainscreen.color=(253/255, 237/255, 221/255, 1)
        #self.layout.remove_widget(self.mainlabel)
        self.layout.remove_widget(self.startbutton)
        self.layout.remove_widget(self.resultspageB)
        #self.layout.remove_widget(self.logintitle)
        #self.layout.remove_widget(self.lemail)
        #self.layout.remove_widget(self.lpassword)
        #self.layout.remove_widget(self.emailinput)
        #self.layout.remove_widget(self.passinput)
        self.layout.add_widget(self.topstrip)
        self.layout.add_widget(self.backbutton1)
        self.layout.add_widget(self.snrbutton)
        self.layout.add_widget(self.morecoming)

    def backtomainscreen(self,events):
        self.mainscreen.color = (60/255, 70/255, 94/255, 1)
        #self.layout.add_widget(self.mainlabel)
        self.layout.add_widget(self.startbutton)
        self.layout.add_widget(self.resultspageB)
        self.layout.remove_widget(self.backbutton1)
        self.layout.remove_widget(self.topstrip)
        self.layout.remove_widget(self.snrbutton)
        self.layout.remove_widget(self.backbutton1)
        self.layout.remove_widget(self.morecoming)

    def updateData(self,*args):
        self.datalist = []
        self.weekdataset = []
        self.monthdataset = []
        self.yeardataset = []
        self.alldataset = []
        self.weekdatasetx = []
        self.monthdatasetx = []
        self.yeardatasetx = []
        self.alldatasetx = []
        usernamestr = str(self.e)
        usernamepos = usernamestr.find('@')
        username = usernamestr[0:usernamepos]
        if db.child(username).shallow().get().val():
            results = db.child(username).get()
            d = []
        #print(results[0])
            for result in results.each():
                datatime = result.key()
                data = result.val()['result']
                # print(datatime)
                timesplited = datatime.split("-")
                d.append(data)
                d.append(timesplited)
                # print(timesplited)
                self.datalist.append(d)
                d = []
            #print(self.datalist)
            now1 = datetime.now()
            self.now = now1
            nowstr = now1.strftime("%m-%d-%Y-%H:%M:%S")
            self.weekday = now1.weekday()
            timesplitedn = nowstr.split("-")
            self.todayTime = timesplitedn
            today_date = self.now.strftime("%d")
            firstdayofweek = int(today_date) - self.weekday
            for x in range(len(self.datalist)):
                if self.datalist[x][1][0] == self.todayTime[0] and self.datalist[x][1][2] == self.todayTime[2] and int(
                        self.datalist[x][1][1]) >= firstdayofweek:
                    datastr = str(self.datalist[x][1][1]) + "   -   " + str(self.datalist[x][0])
                    self.weekdatasetx.append(self.datalist[x][0])
                    self.weekdataset.append(datastr)
            for x in range(len(self.datalist)):
                if self.datalist[x][1][0] == self.todayTime[0] and self.datalist[x][1][2] == self.todayTime[2]:
                    datastr = str(self.datalist[x][1][0]) + "/" + str(self.datalist[x][1][1]) + "   -   " + str(self.datalist[x][0])
                    self.monthdatasetx.append(self.datalist[x][0])
                    self.monthdataset.append(datastr)
            for x in range(len(self.datalist)):
                if self.datalist[x][1][2] == self.todayTime[2]:
                    datastr = str(self.datalist[x][1][0]) + "/" + str(self.datalist[x][1][1]) + "   -   " + str(
                        self.datalist[x][0])
                    self.yeardatasetx.append(self.datalist[x][0])
                    self.yeardataset.append(datastr)
            for x in range(len(self.datalist)):
               self.alldatasetx.append(self.datalist[x][0])

    def maintodata(self,events):
        self.updateData()
        if len(self.datalist)>0:
            self.newscoreL.text="Newest Score: "+str(self.datalist[-1][0])
        else:
            self.newscoreL.text = "Newest Score: None"
        self.mainscreen.color=(253/255, 237/255, 221/255, 1)
        #self.layout.remove_widget(self.mainlabel)
        self.layout.remove_widget(self.startbutton)
        self.layout.remove_widget(self.resultspageB)
        self.layout.add_widget(self.topstrip)
        self.layout.add_widget(self.databacktomain)
        self.layout.add_widget(self.neweststrip)
        self.layout.add_widget(self.newscoreL)
        self.layout.add_widget(self.datadisplay)
        self.layout.add_widget(self.datastrip)
        self.layout.add_widget(self.todaydataB)
        self.layout.add_widget(self.weekdataB)
        self.layout.add_widget(self.monthdataB)
        self.layout.add_widget(self.yeardataB)
        self.layout.add_widget(self.alldataB)
        self.layout.add_widget(self.graphB)

    def datatomain(self,event):
        self.mainscreen.color = (60 / 255, 70 / 255, 94 / 255, 1)
        #self.layout.add_widget(self.mainlabel)
        self.layout.add_widget(self.startbutton)
        self.layout.add_widget(self.resultspageB)
        self.layout.remove_widget(self.topstrip)
        self.layout.remove_widget(self.databacktomain)
        self.layout.remove_widget(self.neweststrip)
        self.layout.remove_widget(self.newscoreL)
        self.layout.remove_widget(self.datadisplay)
        self.layout.remove_widget(self.datastrip)
        self.layout.remove_widget(self.todaydataB)
        self.layout.remove_widget(self.weekdataB)
        self.layout.remove_widget(self.monthdataB)
        self.layout.remove_widget(self.yeardataB)
        self.layout.remove_widget(self.alldataB)
        self.layout.remove_widget(self.graphB)

    def datatograph(self,event):
        self.updateData()
        #self.mainscreen.color = (60 / 255, 70 / 255, 94 / 255, 1)
        self.layout.add_widget(self.graphtodataB)
        self.layout.add_widget(self.weekgraphB)
        self.layout.add_widget(self.monthgraphB)
        self.layout.add_widget(self.yeargraphB)
        self.layout.add_widget(self.allgraphB)
        self.layout.remove_widget(self.databacktomain)
        #self.layout.remove_widget(self.neweststrip)
        self.layout.remove_widget(self.newscoreL)
        self.layout.remove_widget(self.datadisplay)
        self.layout.remove_widget(self.datastrip)
        self.layout.remove_widget(self.todaydataB)
        self.layout.remove_widget(self.weekdataB)
        self.layout.remove_widget(self.monthdataB)
        self.layout.remove_widget(self.yeardataB)
        self.layout.remove_widget(self.alldataB)
        self.layout.remove_widget(self.graphB)
        self.layout.add_widget(self.graph)

    def graphtodata(self,event):
        self.updateData()
        #self.mainscreen.color = (60 / 255, 70 / 255, 94 / 255, 1)
        self.layout.remove_widget(self.graphtodataB)
        self.layout.remove_widget(self.weekgraphB)
        self.layout.remove_widget(self.monthgraphB)
        self.layout.remove_widget(self.yeargraphB)
        self.layout.remove_widget(self.allgraphB)
        self.layout.add_widget(self.databacktomain)
        #self.layout.remove_widget(self.neweststrip)
        self.layout.add_widget(self.newscoreL)
        self.layout.add_widget(self.datadisplay)
        self.layout.add_widget(self.datastrip)
        self.layout.add_widget(self.todaydataB)
        self.layout.add_widget(self.weekdataB)
        self.layout.add_widget(self.monthdataB)
        self.layout.add_widget(self.yeardataB)
        self.layout.add_widget(self.alldataB)
        self.layout.add_widget(self.graphB)
        self.graph.opacity=0
        self.layout.remove_widget(self.graph)

    def todayDataInfo(self, events):
        if self.datadisplay.is_open == False:
            today=[]
            today.append("Time   -   Score")
            for x in range(len(self.datalist)):
                if self.datalist[x][1][0]==self.todayTime[0] and self.datalist[x][1][1]==self.todayTime[1] and self.datalist[x][1][2]==self.todayTime[2]:
                    datastr=str(self.datalist[x][1][-1])+"   -   "+str(self.datalist[x][0])
                    today.append(datastr)
            self.datadisplay.values=today
            self.datadisplay.is_open = True
        else:
            self.datadisplay.is_open = False

    def weekDataInfo(self,events):
        if self.datadisplay.is_open==False:
            today = []
            today.append("Date   -   Score")
            for x in range(len(self.weekdataset)):
                today.append(self.weekdataset[x])
            self.datadisplay.values = today
            self.datadisplay.is_open=True
        else:
            self.datadisplay.is_open=False

    def monthDataInfo(self,events):
        if self.datadisplay.is_open==False:
            today = []
            today.append("Date   -   Score")
            for x in range(len(self.monthdataset)):
                today.append(self.monthdataset[x])
            self.datadisplay.values = today
            self.datadisplay.is_open=True
        else:
            self.datadisplay.is_open=False

    def yearDataInfo(self, events):
        if self.datadisplay.is_open == False:
            today = []
            today.append("Date   -   Score")
            for x in range(len(self.yeardataset)):
                today.append(self.yeardataset[x])
            self.datadisplay.values = today
            self.datadisplay.is_open = True
        else:
            self.datadisplay.is_open = False

    def allDataInfo(self,events):
        if self.datadisplay.is_open==False:
            today = []
            today.append("Date   -   Score")
            for x in range(len(self.datalist)):
                datastr = str(self.datalist[x][1][0]) +"/"+str(self.datalist[x][1][1]) +"/"+str(self.datalist[x][1][2]) + "   -   " + str(self.datalist[x][0])
                today.append(datastr)
            self.datadisplay.values = today
            self.datadisplay.is_open=True
        else:
            self.datadisplay.is_open=False

    def snrbacktomain(self,events):
        self.countdownnum = 10
        self.countdown.text = str(10)
        self.snrprogress.value = 0
        self.points = []
        self.mainscreen.color = (60 / 255, 70 / 255, 94 / 255, 1)
        #self.layout.add_widget(self.mainlabel)
        self.layout.add_widget(self.startbutton)
        self.layout.add_widget(self.resultspageB)
        self.layout.remove_widget(self.snrback)
        self.layout.remove_widget(self.snrdoneresult)
        self.layout.remove_widget(self.redobutton)
        now1 = datetime.now()
        nowstr=now1.strftime("%m-%d-%Y-%H:%M:%S")
        usernamestr=str(self.e)
        #print(usernamestr)
        usernamepos=usernamestr.find('@')
        #print(usernamepos)
        username=usernamestr[0:usernamepos]
        data={'result':str(self.resultnum)}
        db.child(username).child(nowstr).set(data)

    def graphsets(self,set):
        if len(set) > 1:
            same = 0
            for x in range(len(set) - 1):
                if set[x] == set[x + 1]:
                    same += 1
            self.graph.xmax = len(set)-1
            self.graph.ymin = min(set)
            if same == 0:
                self.graph.ymax = max(set)
            else:
                self.graph.ymax = 0.1+float(max(set))
            self.plot.points = [(x, float(set[x])) for x in range(len(set))]
            self.graph.add_plot(self.plot)

    def weekGraph(self,event):
        #print(self.weekdatasetx)
        if self.graph.opacity==0:
            self.graphsets(self.weekdatasetx)
            self.graph.opacity = 1
        else:
            self.graph.opacity=0
            self.graph.remove_plot(self.plot)

    def monthGraph(self,event):
        #print(self.monthdatasetx)
        if self.graph.opacity==0:
            self.graphsets(self.monthdatasetx)
            self.graph.opacity = 1
        else:
            self.graph.opacity=0
            self.graph.remove_plot(self.plot)

    def yearGraph(self,event):
        if self.graph.opacity==0:
            self.graphsets(self.yeardatasetx)
            self.graph.opacity = 1
        else:
            self.graph.opacity=0
            self.graph.remove_plot(self.plot)

    def allGraph(self,event):
        if self.graph.opacity==0:
            self.graphsets(self.alldatasetx)
            self.graph.opacity = 1
        else:
            self.graph.opacity=0
            self.graph.remove_plot(self.plot)

    def menutoSNRI(self,event):
        self.layout.add_widget(self.SNRItomenuB)
        self.layout.add_widget(self.SNRItoCountB)
        self.layout.add_widget(self.SNRlabel)
        self.layout.add_widget(self.SNRinstr)
        self.layout.add_widget(self.SNRIwarning)
        self.layout.remove_widget(self.topstrip)
        self.layout.remove_widget(self.snrbutton)
        self.layout.remove_widget(self.backbutton1)
        self.layout.remove_widget(self.morecoming)

    def SNRItomenu(self,event):
        self.layout.remove_widget(self.SNRItomenuB)
        self.layout.remove_widget(self.SNRItoCountB)
        self.layout.remove_widget(self.SNRlabel)
        self.layout.remove_widget(self.SNRinstr)
        self.layout.remove_widget(self.SNRIwarning)
        self.layout.add_widget(self.topstrip)
        self.layout.add_widget(self.snrbutton)
        self.layout.add_widget(self.backbutton1)
        self.layout.add_widget(self.morecoming)

    def countdowntimer(self,event):
        self.mainscreen.color = (0,0,0, 1)
        self.layout.add_widget(self.countdown)
        self.layout.remove_widget(self.SNRItomenuB)
        self.layout.remove_widget(self.SNRItoCountB)
        self.layout.remove_widget(self.SNRlabel)
        self.layout.remove_widget(self.SNRinstr)
        self.layout.remove_widget(self.SNRIwarning)
        self.event=Clock.schedule_interval(self.countdownnumdecrease, 1)

    def countdownnumdecrease(self, *args):
        if self.countdownnum>0:
            self.countdownnum-=1;
            self.countdown.text=str(self.countdownnum)
        else:
            Clock.unschedule(self.event)
            self.layout.remove_widget(self.countdown)
            self.layout.add_widget(self.webcam)
            self.layout.add_widget(self.snrprogress)
            self.capture = cv2.VideoCapture(0)
            self.event2=Clock.schedule_interval(self.update, 1.0 / 33.0)

    def nparray(self,landmarks):
        return np.array([landmarks.x, landmarks.y, landmarks.z])

    def update(self, *args):
        cap = self.capture
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            ret, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            #width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            #height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            #print(width)
            #print(height)
            # Make Detections
            results = holistic.process(image)
            # Recolor image back to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # Draw landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2))
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=2))
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2))
        buf = cv2.flip(image, 0).tostring()
        texture1 = Texture.create(size=(image.shape[1] , image.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.webcam.texture=texture1
        count = 0
        if results.pose_landmarks != None:
            hipl = results.pose_world_landmarks.landmark[23]
            feetl = results.pose_world_landmarks.landmark[31]
            indexl = results.pose_world_landmarks.landmark[11]
            hipln = self.nparray(hipl)
            feetln = self.nparray(feetl)
            indexln = self.nparray(indexl)
            a = feetln - hipln
            b = feetln - indexln
            d = a.dot(b) / np.linalg.norm(a) ** 2
            # print(hipl.visibility)
            if hipl.visibility > 0.90 and feetl.visibility > 0.90 and indexl.visibility > 0.90:
                self.points.append(d)
                self.snrprogress.value=len(self.points)
                #print(d)
            if len(self.points) > 19:
                Clock.unschedule(self.event2)
                self.capture.release()
                D = self.points[0]
                for i in range(len(self.points) - 1):
                    num = D * .99 + self.points[i + 1] * 0.01
                    D = num
                n = round(D,1)
                diff = n - D
                R = 0
                if (diff > 0):
                    if (diff < 0.25):
                        R = n
                    else:
                        R = n - 0.5
                else:
                    if (diff > -0.25):
                        R = n
                    else:
                        R = n + 0.5
                self.mainscreen.color= (60 / 255, 70 / 255, 94 / 255, 1)
                self.layout.remove_widget(self.webcam)
                self.layout.remove_widget(self.snrprogress)
                self.resultnum=n
                self.snrdoneresult.text=str(self.resultnum)
                self.layout.add_widget(self.snrdoneresult)
                self.layout.add_widget(self.snrback)
                self.layout.add_widget(self.redobutton)

    def redotest(self,*args):
        self.countdownnum = 10
        self.countdown.text = str(10)
        self.snrprogress.value=0
        self.points=[]
        self.layout.remove_widget(self.snrdoneresult)
        self.layout.remove_widget(self.snrback)
        self.layout.remove_widget(self.redobutton)
        self.mainscreen.color = (0, 0, 0, 1)
        self.layout.add_widget(self.countdown)
        self.event = Clock.schedule_interval(self.countdownnumdecrease, 1)
if __name__ == '__main__':
    KivyApp().run()
    cv2.destroyAllWindows()
