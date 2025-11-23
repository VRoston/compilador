from gui import MVD_GUI
from core import MVD

if __name__ == "__main__":
    try:
        app = MVD_GUI()
        # cria e injeta a MVD no GUI antes de iniciar a janela
        app.mvd = MVD()
        app.mainloop()
    except Exception as e:
        print(f"Erro fatal ao iniciar a GUI: {e}")