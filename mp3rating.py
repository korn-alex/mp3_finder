from pathlib import Path
import os, sys
# windows for python38 "libvlc.dll" is necessary
if sys.platform == 'windows':
    os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
from tkinter import Tk, Frame, Listbox, filedialog, Button, END, Menu, IntVar
from tkinter.ttk import Progressbar
from pathlib import Path
import re
import vlc
from pprint import pprint
from time import sleep
from functools import partial
from overlay import PlayerControl


app = Tk()
app.geometry("300x300")
app.minsize(width=600,height=300)
app.title('Quick MP3 Finder')


if getattr(sys, 'frozen', False):
    CWD = Path(sys._MEIPASS)
else:
    # we are running in a normal Python environment
    CWD = Path(__file__).parent

class Entry:
    def __init__(self, file_id, file):
        self.id = str(file_id)
        self.file = file
        self.is_fav = False
        self._update_text()
    
    def _update_text(self):
        fav = 'X' if self.is_fav else ' '
        self.text = f'{int(self.id):<4d}| {fav} | {str(self.file)}'

    @property
    def favorite(self):
        return self.is_fav
    
    @favorite.setter
    def favorite(self, is_favorite):
        self.is_fav = is_favorite
        self._update_text()
        
class MainFrame(Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.pack(expand=True, fill='both')

class FindBtn(Button):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.pack()

class FinderBox(Listbox):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.pack(expand=True, fill='both')
        self.entries = None
    
    def selectpath(self):
        d = filedialog.askdirectory()
        self.searchpath = Path(d)
        self.search()
    
    def search(self):
        try:
            if self.mp3:
                self.mp3.stop()
        except Exception as e:
                print('no current mp3 playing', e)
        results = self.searchpath.rglob('**/*.mp3')
        if not self.entries:
            self.entries = []
            for i, r in enumerate(results):
                entry = Entry(i, r)
                self.entries.append(entry)
                self.insert(END, entry.text)
                self.yview(END)
                self.update()
        else:
            filenames = {str(e.file):id for id, e in enumerate(self.entries)}
            #print('filenames')
            #pprint(filenames)
            for i, r in enumerate(results):
                #print('result', r)
                file_id = filenames.get(str(r))
                print(file_id)
                #filenames[r]=222
                if file_id:
                    entry = self.entries[file_id]
                    self.delete(file_id)
                    self.insert(file_id, entry.text)
                else:
                    entry = Entry(i, r)
                    self.entries.append(entry)
                    self.insert(END, entry.text)
                    self.yview(END)
                    self.update()              
            print('filenames')
            pprint(filenames)
        self._mp3_as_uri()
        self.mp3 = vlc.MediaPlayer(self.current_mp3uri)
        

    def _mp3_as_uri(self):
        f = self.entries[self.current_mp3id].file
        fp = Path(f)
        self.current_mp3uri = fp.as_uri()
        print(fp)
        print(type(fp))
        print(self.current_mp3uri)

class Controller(FinderBox):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.bind('<space>', func=self.play)
        self.bind('<Up>', func=self.prev)
        self.bind('<Down>', func=self.next)
        self.bind('<Right>', func=self.forward)
        self.bind('<Left>', func=self.backward)
        self.bind('<Return>', func=self.change_favorite)
        self.bind('<t>', func=self.test)
        self.current_mp3id = 0
        self.next_mp3id = 1
        self.mp3 = vlc.MediaPlayer()
        self.started = False

    def play(self, *event):
        print('selection: ',self.curselection())
        # id = self.current_mp3id
        # nid = self.next_mp3id
        sid, *_ = self.curselection()
        cid = self.current_mp3id
        # self.activate(nid)
        print(sid, cid)
        if sid != cid:
            # self.activate(nid)
            self.mp3.stop()
            self.current_mp3id = sid
            # self.activate(nid)
            self._mp3_as_uri()
            uri = self.current_mp3uri
            self.mp3 = vlc.MediaPlayer(uri)
            self.mp3.play()
            self.started = True
        else:
            if self.mp3.is_playing():
                self.mp3.pause()
            else:
                self.mp3.play()
                # self.started = True


    def next(self, *event):
        # id = self.current_mp3id
        id, *_ = self.curselection()
        nid = id + 1
        self.selection_clear(id)
        if nid > (self.size()-1):
            self.next_mp3id = 0
            self.selection_set(0)
            self.activate(0)
        else:
            self.next_mp3id = nid
            self.selection_set(nid)

    
    def prev(self, *event):
        # id = self.current_mp3id
        id, *_ = self.curselection()
        nid = id - 1
        self.selection_clear(id)
        if nid < 0:
            last_id = (self.size()-1)
            # print('last id ', last_id)
            # self.unbind('<Up>')
            self.next_mp3id = last_id
            self.activate(last_id)
            self.selection_set(last_id)
        else:
            self.next_mp3id = nid
            # self.activate(nid)
            self.selection_set(nid)

    def forward(self, *event):
        ct = self.mp3.get_time()
        length = self.mp3.get_length()
        nt = ct + 1000
        if nt > length:
            self.mp3.stop()
            return
        self.mp3.set_time(nt)
    
    def backward(self, *event):
        ct = self.mp3.get_time()
        length = self.mp3.get_length()
        nt = ct - 1000
        if nt < 0:
            nt = 0
        self.mp3.set_time(nt)

    def change_favorite(self, *event):
        # id = self.current_mp3id
        id, *_ = self.curselection()
        # selection = self.curselection()
        track = self.entries[id]
        fav = track.favorite
        if fav:
            track.favorite = False
        else:
            track.favorite = True
        self.selection_clear(id)
        self.delete(id)
        self.insert(id, track.text)
        self.activate(id)
        self.selection_set(id)
    
    def export(self, name=None):
        """Export to m3u playlist."""
        if not name:
            name = 'playlist.m3u'
            filepath = Path.cwd() / name
            # print('filepath:', filepath)
            # print('Path.cwd()',Path.cwd())
        with open(filepath, 'w') as f:
            for entry in self.entries:
                if entry.favorite:
                    f.write(str(entry.file))
                    f.write('\n')
        print('Playlist exported to: ', filepath)

    def import_playlist(self, importpath=None):
        """Imports from m3u file"""
        if not importpath:
            initialdir = Path.cwd()
            playlistpath = filedialog.askopenfile(initialdir=initialdir, filetypes = (("Playlist","*.m3u"),("all files","*.*")))
        print('reading', playlistpath)
        playlist = Path(playlistpath.name)
        with open(playlist, 'r') as f:
            if not self.entries:
                filenames=dict()
                self.entries = list()
                last_id = 0
            else:
                filenames = {str(e.file):id for id, e in enumerate(self.entries)}
                last_id = len(self.entries)-1
            lines = f.read().splitlines()
            for line in lines:
                print(line)
                file_id = filenames.get(line)
                if file_id:
                    entry = self.entries[file_id]
                    entry.favorite = True
                    self.delete(file_id)
                    self.insert(file_id, entry.text)
                else:                	
                	entry = Entry(last_id, line)
                	entry.favorite = True
                	self.entries.append(entry)
                	self.insert(last_id, entry.text)
                	last_id += 1        

    def test(self, *event):
        self.selection_set(14)
        self.activate(14)

mf = MainFrame(master=app)
m1 = Menu(master=app)
app.config(menu=m1)
ctrl = Controller(master=mf, yscrollcommand=True)
m1.add_command(label='Search', command=ctrl.selectpath)
m1.add_command(label='Export', command=ctrl.export)
import_cmd = partial(ctrl.import_playlist, importpath=None)
m1.add_command(label='Import', command=import_cmd)

control = PlayerControl(master=mf, box=ctrl, autoplay=True)
app.mainloop()