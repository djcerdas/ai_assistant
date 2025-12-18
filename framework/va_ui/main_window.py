# va_ui/main_window.py
import tkinter as tk
from tkinter import ttk
from typing import Optional

from va_services.runtime import VisualAssistantApplication


class MainWindow(tk.Tk):
    def __init__(self, app_core: VisualAssistantApplication):
        super().__init__()
        self.app_core = app_core

        # Configuración básica de la ventana
        self.title("Visual Assistant V1 - Framework")
        self.geometry("600x400")
        self.resizable(False, False)

        # Variables de estado para mostrar en la UI
        self.status_var = tk.StringVar(value="Estado: detenido")
        self.session_var = tk.StringVar(value="Sesión actual: -")
        self.last_frame_var = tk.StringVar(value="Último frame almacenado: -")

        # Flag interno para saber si el loop está activo
        self._loop_running: bool = False

        # Construir los controles
        self._build_widgets()

    def _build_widgets(self) -> None:
        padding = {"padx": 10, "pady": 10}

        # --- Fila de botones ---
        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(side=tk.TOP, fill=tk.X, **padding)

        btn_start = ttk.Button(
            frame_buttons,
            text="Iniciar asistente",
            command=self.on_start
        )
        btn_stop = ttk.Button(
            frame_buttons,
            text="Detener asistente",
            command=self.on_stop
        )
        btn_exit = ttk.Button(
            frame_buttons,
            text="Salir",
            command=self.destroy
        )

        btn_start.pack(side=tk.LEFT, **padding)
        btn_stop.pack(side=tk.LEFT, **padding)
        btn_exit.pack(side=tk.RIGHT, **padding)

        # --- Área de estado ---
        frame_status = ttk.Frame(self)
        frame_status.pack(side=tk.TOP, fill=tk.BOTH, expand=True, **padding)

        lbl_status = ttk.Label(frame_status, textvariable=self.status_var)
        lbl_session = ttk.Label(frame_status, textvariable=self.session_var)
        lbl_frame = ttk.Label(frame_status, textvariable=self.last_frame_var)

        lbl_status.pack(anchor="w", pady=5)
        lbl_session.pack(anchor="w", pady=5)
        lbl_frame.pack(anchor="w", pady=5)

    # ================== Callbacks de botones ==================

    def on_start(self) -> None:
        """Callback del botón 'Iniciar asistente'."""
        self.app_core.start()
        self.status_var.set("Estado: ejecutándose")

        if self.app_core.current_session_id is not None:
            self.session_var.set(
                f"Sesión actual: {self.app_core.current_session_id}"
            )

        if not self._loop_running:
            self._loop_running = True
            # Programar el primer tick del loop
            self.after(self.app_core.main_loop_interval_ms, self._loop_tick)

    def on_stop(self) -> None:
        """Callback del botón 'Detener asistente'."""
        self.app_core.stop()
        self.status_var.set("Estado: detenido")
        self._loop_running = False
        self.session_var.set("Sesión actual: -")

    # ================== Bucle tipo "Main Loop" ==================

    def _loop_tick(self) -> None:
        """
        Este método se llama periódicamente usando Tkinter.after y simula
        el ciclo principal del asistente. Aquí se ejecuta run_single_cycle()
        y se actualiza la UI con el último frame.
        """
        if not self.app_core.is_running:
            self._loop_running = False
            return

        frame_id: Optional[int] = self.app_core.run_single_cycle()
        if frame_id is not None:
            self.last_frame_var.set(f"Último frame almacenado: {frame_id}")

        # Reprogramar el siguiente ciclo
        self.after(self.app_core.main_loop_interval_ms, self._loop_tick)


def run_app() -> None:
    """Punto de entrada de la UI: crea la app core y la ventana."""
    app_core = VisualAssistantApplication()
    window = MainWindow(app_core)
    window.mainloop()

