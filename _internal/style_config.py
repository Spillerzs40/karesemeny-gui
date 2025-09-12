import ttkbootstrap as tb

def setup_style(style, betumeret=12):
    # style paraméter: a már létező tb.Style() objektumot várjuk, nem csinálunk újat

    default_font = ('Segoe UI', betumeret)
    style.configure('.', font=default_font)
    style.configure('TLabel', font=default_font)
    style.configure('TButton', font=default_font)
    style.configure('TEntry', font=default_font)
    style.configure('TCombobox', font=default_font)
    style.configure('Treeview', font=default_font, rowheight=28)
    style.configure('TCombobox', padding=3)

    style.configure('TCheckbutton',
                    font=default_font,
                    padding=2,
                    indicatorrelief='flat',
                    indicatorsize=15)
    style.map('TCheckbutton',
              background=[('active', '#dbe9ff'), ('!active', '#f0f2f5')],
              foreground=[('selected', '#004080')],
              indicatorcolor=[('selected', '#5a85d6')])

    style.configure('Accent.TButton',
                    font=('Segoe UI', 12, 'bold'),
                    foreground='white',
                    background='#d7e3fa',
                    borderwidth=0,
                    focusthickness=2,
                    focuscolor='none',
                    padding=6,
                    relief='flat')
    style.map('Accent.TButton',
              background=[('active', '#c1d1f7'), ('!disabled', '#d7e3fa')])

    style.configure('Treeview',
                    font=default_font,
                    background='white',
                    foreground='black',
                    fieldbackground='white',
                    bordercolor='#cbd5e0',
                    borderwidth=1,
                    rowheight=28)
    style.map('Treeview',
              background=[('selected', '#a7c7ff')])

    style.configure('Treeview.Heading',
                    font=('Segoe UI', 11, 'bold'),
                    background='#d7e3fa',
                    foreground='#003366',
                    relief='flat')
    style.map('Treeview.Heading',
              background=[('active', '#c1d1f7'), ('pressed', '#a8bff2')])

    # NEM kell visszatérni semmit, mert a style-t módosítja