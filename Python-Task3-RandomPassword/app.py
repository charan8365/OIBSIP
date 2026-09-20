import secrets
import string
import tkinter as tk
from tkinter import messagebox

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Random Password Generator - OIBSIP')
        self.root.geometry('760x520')
        self.root.resizable(False, False)
        self.length_var = tk.IntVar(value=12)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text='Random Password Generator', font=('Arial', 24, 'bold')).pack(pady=(25,5))
        tk.Label(self.root, text='OASIS INFOBYTE • Python Programming • Task 3', font=('Arial',11)).pack(pady=(0,20))
        options = tk.LabelFrame(self.root, text='Password Options', padx=20, pady=15, font=('Arial',11,'bold'))
        options.pack(fill='x', padx=35)
        tk.Label(options, text='Password Length:').grid(row=0,column=0,sticky='w',padx=8,pady=8)
        tk.Spinbox(options, from_=4, to=64, textvariable=self.length_var, width=8, font=('Arial',11)).grid(row=0,column=1,sticky='w',padx=8,pady=8)
        tk.Checkbutton(options,text='Uppercase (A-Z)',variable=self.upper_var).grid(row=1,column=0,sticky='w',padx=8)
        tk.Checkbutton(options,text='Lowercase (a-z)',variable=self.lower_var).grid(row=1,column=1,sticky='w',padx=8)
        tk.Checkbutton(options,text='Numbers (0-9)',variable=self.digits_var).grid(row=2,column=0,sticky='w',padx=8)
        tk.Checkbutton(options,text='Symbols (!@#$)',variable=self.symbols_var).grid(row=2,column=1,sticky='w',padx=8)
        tk.Label(self.root,text='Generated Password',font=('Arial',12,'bold')).pack(anchor='w',padx=38,pady=(25,5))
        tk.Entry(self.root,textvariable=self.password_var,font=('Consolas',16),justify='center',state='readonly',readonlybackground='white').pack(fill='x',padx=38,ipady=10)
        self.strength_label=tk.Label(self.root,text='Password strength: —',font=('Arial',11,'bold'))
        self.strength_label.pack(pady=10)
        buttons=tk.Frame(self.root); buttons.pack(pady=8)
        tk.Button(buttons,text='Generate Password',command=self.generate_password,width=18).grid(row=0,column=0,padx=5)
        tk.Button(buttons,text='Copy',command=self.copy_password,width=12).grid(row=0,column=1,padx=5)
        tk.Button(buttons,text='Clear',command=self.clear_password,width=12).grid(row=0,column=2,padx=5)
        tk.Label(self.root,text='Use a long password with a mix of letters, numbers and symbols.',font=('Arial',10)).pack(pady=(18,0))
        tk.Label(self.root,text='Ready',anchor='w',relief='sunken').pack(side='bottom',fill='x')

    def generate_password(self):
        try: length=int(self.length_var.get())
        except (ValueError,tk.TclError):
            messagebox.showerror('Invalid Length','Enter a valid password length.'); return
        if length<4 or length>64:
            messagebox.showerror('Invalid Length','Password length must be between 4 and 64 characters.'); return
        pools=[]
        if self.upper_var.get(): pools.append(string.ascii_uppercase)
        if self.lower_var.get(): pools.append(string.ascii_lowercase)
        if self.digits_var.get(): pools.append(string.digits)
        if self.symbols_var.get(): pools.append(string.punctuation)
        if not pools:
            messagebox.showerror('No Character Types','Select at least one character type.'); return
        if length<len(pools):
            messagebox.showerror('Length Too Short','Increase the length so every selected character type can be used.'); return
        chars=[secrets.choice(pool) for pool in pools]
        all_chars=''.join(pools)
        chars.extend(secrets.choice(all_chars) for _ in range(length-len(chars)))
        for i in range(len(chars)-1,0,-1):
            j=secrets.randbelow(i+1); chars[i],chars[j]=chars[j],chars[i]
        password=''.join(chars); self.password_var.set(password); self.update_strength(password)

    def update_strength(self,password):
        score=sum([len(password)>=8,len(password)>=12,any(c.isupper() for c in password),any(c.islower() for c in password),any(c.isdigit() for c in password),any(c in string.punctuation for c in password)])
        level='Weak' if score<=2 else ('Medium' if score<=4 else 'Strong')
        self.strength_label.config(text=f'Password strength: {level}')

    def copy_password(self):
        password=self.password_var.get()
        if not password:
            messagebox.showwarning('Nothing to Copy','Generate a password first.'); return
        self.root.clipboard_clear(); self.root.clipboard_append(password); self.root.update()
        messagebox.showinfo('Copied','Password copied to the clipboard.')

    def clear_password(self):
        self.password_var.set(''); self.strength_label.config(text='Password strength: —')

if __name__=='__main__':
    root=tk.Tk(); PasswordGeneratorApp(root); root.mainloop()
