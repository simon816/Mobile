from simon816 import text
from simon816.ArgumentParser import *
from traceback import extract_tb as et
appuifw=text.appuifw
import sys,e32
class Console(text.text):
 class err:
   def __init__(self,i):
     self.i=i
   def write(self,l):
     self.i.write(l,True)
 def prev(self):
  if self.history==[]:
   appuifw.note(u'No previous commands','error')
   return
  def nav():
   cmd=self.history[appuifw.app.body.current()]
   self.display()
   self.t.set_pos(self.t.len())
   self.css(self.bodystyle['input'],method='default',apply=1)
   self.t.add(self.toUnicode(cmd))
  lb=appuifw.Listbox(self.history,nav)
  appuifw.app.body=lb
  appuifw.app.exit_key_handler=self.display
 def write(self,line,err=False):
   if err:s='error'
   else:s='printer'
   self.css(self.bodystyle[s],method='default',apply=1)
   self.t.add(self.toUnicode(line))
 def readline(self):
  return self.prompt()
 def console(self,linefeed,i='Blank Console Application 0.1 running'):
  self.version=1.0
  self.author='Simon816'
  #text.text related settings#
  self.saveallowed=0 
  del self.menu[0],self.menu[0],self.menu[2]
  self.menu.insert(0,(u'History',self.prev))
  self.menu.insert(1,(u'Clear buffer',self.clear))
  self.menu.append((u'Exit',self.quit))
  self.bind('exit',self.quit)
  self.bind('key',self.press)
  del self.bindable[self.bindable.index('exit')]
  self.bindable.append('shell_exit') #exit handler remapped to shell_exit
  self.bindable.append('exec_cmd')
  self.bind('exec_cmd',lambda c:None)
  self.bind('shell_exit',lambda *_:None)
  self.bindable.append('tab_press')
  self.bind('tab_press', lambda l:None)
  self.bodystyle={
   'input':{},
   'output':{},
   'prompter':{},
   'printer':{},
   'error':{'color':'#DF2020'}
  }
  # = = #
  # GUI Control #
  self.oldstd={
   'out':sys.stdout,
   'err':sys.stderr,
   'in':sys.stdin,
   'body':appuifw.app.body,
   'exit':appuifw.app.exit_key_handler,
   'menu':appuifw.app.menu
    }
  sys.stdout=self
  sys.stderr=self.err(self)
  sys.stdin=self
  if hasattr(linefeed, '__call__'):
    self.lf=linefeed
  else:
    self.lf=lambda:linefeed
  self.master_lock=e32.Ao_lock() #lock for python instance
  self.lock=e32.Ao_lock() #lock for internal use
  # = = #
  py,os='.'.join(map(str,sys.version_info[:-2])),sys.platform
  v,a=self.version,self.author
  self.intro='Console Interface by %s Version %.1f\nRunning Python %s on %s\n%s\n'%(a,v,py,os,i)
  self.history=[]
  self.promptText=''
  self.promptMode=False
  self.promptLine=''
  return self
 def shell_run(self,starttext=None):
  self.clear()
  self.display()
  if starttext:
   self.t.add(self.toUnicode(starttext))
  self.master_lock.wait()
 def quit(self):
  sys.stdout=self.oldstd['out']
  sys.stderr=self.oldstd['err']
  sys.stdin=self.oldstd['in']
  self.lock.signal()
  self.master_lock.signal()
  appuifw.app.body=self.oldstd['body']
  appuifw.app.exit_key_handler=self.oldstd['exit']
  appuifw.app.menu=self.oldstd['menu']
  self.on('shell_exit')
 def clear(self):
  self.t.clear()
  self.css(self.bodystyle['printer'],method='default',apply=1)
  self.t.add(self.toUnicode(self.intro))
  self.newline()
 def newline(self):
  self.css(self.bodystyle['prompter'],method='default',apply=1)
  self.t.add(self.toUnicode(self.lf()))
  self.css(self.bodystyle['input'],method='default',apply=1)
  self.t.add(self.toUnicode(' '))

 def prompt(self,text='',protect=0):
  self.promptMode=1
  if text:
   self.css(self.bodystyle['prompter'],method='default',apply=1)
   self.t.add(self.toUnicode(text))
   self.promptLine=text
  if protect:self.promptMode=2
  self.lock.wait()
  #this is held, returns when lock is given the signal()
  text=self.promptText
  self.promptText=''
  self.promptLine=''
  return text
 def output(self,text):
  self.css(self.bodystyle['output'],method='default',apply=1)
  self.t.add(self.toUnicode(text))
 def press(self,key,info):
  after=[]
  def onafter():
    for f in after:
        try:f()
        except:
            import traceback
            traceback.print_exc()
  lines=self.getText().split('\r\n')
  line=lines[-1]
  if self.promptMode:
   if key==13:
    self.lock.signal()
    self.promptMode=False
    return
   if info[0]=='backspace':
     pl=self.promptLine
     cpos=self.t.get_pos()
     if self.t.get(cpos-len(pl),len(pl))==unicode(pl):
      self.t.add(u' ')
      return
     self.promptText=self.promptText[:-1]
   else:
    if not self.promptLine:self.promptLine=self.getText().split('\r\n')[-1]
    self.promptText+=str(info[1])
   if self.promptMode==2:
    def hide():
     self.t.delete(self.t.len()-1,1)#remove typed letter
     self.t.add(u'*')# add * in place
    after.append(hide)
  elif key==13: #enter pressed
   self.t.set_pos(self.t.len())
   lfl=len(self.lf())+1 # +1 for added space
   if line and line[-1]=='\\':
    after.append(lambda:self.t.add(u' '*lfl))
   else:
    if lines[-2] and lines[-2][-1]=='\\' and line[:lfl]==' '*lfl:
     rev=[l for l in lines]
     rev.reverse()
     prev=[]
     for l in rev[1:]:
      if not l[-1]=='\\':break
      pre=l[lfl:-1]
      prev.append(pre)
     prev.reverse()
     line=self.lf()+' '+''.join(prev)+line[lfl:]
    cmd=line[lfl:]
    if cmd:
     if cmd in self.history:
      del self.history[self.history.index(cmd)]
     self.history.insert(0,cmd)
     after.append(lambda:self.on('exec_cmd',cmd))
    after.append(self.newline)
  elif info[0]=='backspace':
   cpos=self.t.get_pos()
   c=u''
   while c!=u'\u2029':
     c=self.t.get(cpos,1)
     cpos-=1
   line=self.t.get(cpos+2,self.t.get_pos()-1)
   if line == unicode(self.lf()+' '):
     self.t.add(u' ')
  if after is not []:e32.ao_sleep(0,onafter)
  if info[0]=='tab':
    l=self.t.getText().split('\r\n')
    self.on('tab_press',l[-1])

def test():
 c=Console()
 c.console('>>>')
 def dostuff(cmd):
  if cmd=='prompt':
   print 'you typed:'+raw_input('type something >')
  elif cmd == 'password':
   print 'your password is:'+c.prompt('Enter password>',1)
  else:
   print 'the command is:'+ cmd
 c.bind('exec_cmd',dostuff)
 c.shell_run('prompt')
if __name__ == '__main__':
   test()