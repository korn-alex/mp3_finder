from tkinter import Button, Label, Frame, DoubleVar, StringVar
from tkinter.ttk import Progressbar
from vlc import State

class Progress(Progressbar):
    def __init__(self, master=None, box=None, autoplay=True, **kw):
        super().__init__(master=master, **kw)
        self.box = box
        self.time = DoubleVar(master=master, value=0)
        self.timestr = StringVar(master=master, value='Current MP3:')
        self.current_mp3id_str = StringVar(master=master, value='')
        self.pb = Progressbar(master=master, variable=self.time)
        # self.pb['value'] = self.time.get()
        # self.pb['maximum'] = self.length.get()
        self.label = Label(master=master, textvariable=self.timestr, text='Current MP3:')
        self.label.pack()
        self.current_mp3id = Label(master, textvariable=self.current_mp3id_str)
        self.current_mp3id.pack()
        self.pb.pack()
        # self.started = False
        self.update(autoplay=autoplay)
    
    def update(self, autoplay=True):
        if not self.box.started:
            pass
        else:
            mp3id = self.box.current_mp3id
            time = self.box.mp3.get_time()/1000
            length = self.box.mp3.get_length()/1000
            timestr = f'{time:.2f} / {length:.2f}'
            self.time.set(time)
            self.timestr.set(timestr)
            self.current_mp3id_str.set(f'Current MP3: {mp3id}')
            # self.length.set(self.box.mp3.get_length())
            self.pb['maximum'] = length
            if self.box.mp3.get_state()==State.Ended:
                self.timestr.set(f'{length:.2f} / {length:.2f}')
                if autoplay:
                    self.box.next()
                    self.box.play()
            # print('update ',timestr)
            try:
                print(self.mp3)
            except:
                pass
            # self.length = self.box.mp3.get_length()
        self.after(100, func=self.update)

class PlayerControl(Frame):
    def __init__(self, master=None, box=None, autoplay=True, **kw):
        self.pb = Progress(master=master, box=box, autoplay=autoplay, **kw)