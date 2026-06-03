"""
ui.py — Full application UI built with CustomTkinter.
Uses ONLY pack geometry manager throughout.
Supports 6 named themes (dark + light variants).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from constants import (
    APP_NAME, APP_SUBTITLE, RATIO_OPTIONS,
    THEMES, THEME_NAMES, DEFAULT_THEME,
)
from trig_engine import compute, quadrant_label, astc_label, TrigResult
from history import HistoryManager
from conversions import deg_to_rad, deg_to_grad


class TrigExplorerApp(ctk.CTk):

    def __init__(self) -> None:
        super().__init__()

        self._theme_name = DEFAULT_THEME
        self._history = HistoryManager()
        self._last_result: TrigResult | None = None
        self._advanced_open = False

        self._apply_ctk_mode()

        self.title(APP_NAME)
        self.geometry("1200x860")
        self.minsize(920, 700)
        self.resizable(True, True)

        self._build_ui()

        self.bind("<Control-c>",       lambda e: self._copy_result())
        self.bind("<Control-Shift-C>", lambda e: self._copy_all())
        self.bind("<Control-h>",       lambda e: self._clear_history())
        self.bind("<Control-e>",       lambda e: self._export_csv())

        self._on_change()

    # ── theme shorthand ───────────────────────────────────────────────────────
    @property
    def t(self) -> dict:
        return THEMES[self._theme_name]

    def _apply_ctk_mode(self) -> None:
        mode = THEMES[self._theme_name].get("mode", "dark")
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")

    # ─────────────────────────────────────────────────────────────────────────
    # BUILD
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        t = self.t
        self.configure(fg_color=t["bg"])

        # ── Header ────────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=t["surface"], corner_radius=0, height=68)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        self._lbl_title = ctk.CTkLabel(
            hdr, text=f"  ∿  {APP_NAME}",
            font=ctk.CTkFont("Georgia", 26, "bold"),
            text_color=t["accent"],
        )
        self._lbl_title.pack(side="left", padx=24)

        self._lbl_sub = ctk.CTkLabel(
            hdr, text=APP_SUBTITLE,
            font=ctk.CTkFont("Helvetica", 13),
            text_color=t["text_sub"],
        )
        self._lbl_sub.pack(side="left", padx=8)

        # Theme selector (right side of header)
        theme_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        theme_frame.pack(side="right", padx=20)

        ctk.CTkLabel(
            theme_frame, text="Theme:",
            font=ctk.CTkFont("Helvetica", 12),
            text_color=t["text_sub"],
        ).pack(side="left", padx=(0, 6))

        self._theme_var = ctk.StringVar(value=self._theme_name)
        self._theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self._theme_var,
            values=THEME_NAMES,
            font=ctk.CTkFont("Helvetica", 12),
            fg_color=t["surface2"],
            button_color=t["accent"],
            button_hover_color=t["accent2"],
            text_color=t["text"],
            width=130, height=32,
            command=self._on_theme_change,
        )
        self._theme_menu.pack(side="left")

        # ── Body ─────────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=t["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=10)

        self._left = ctk.CTkScrollableFrame(
            body, fg_color=t["bg"], width=320,
            scrollbar_button_color=t["border"],
            scrollbar_fg_color=t["bg"],
            corner_radius=0,
        )
        self._left.pack(side="left", fill="y", padx=(0, 8))

        self._right = ctk.CTkFrame(body, fg_color=t["bg"])
        self._right.pack(side="left", fill="both", expand=True)

        self._build_input_panel()
        self._build_conversion_card()
        self._build_advanced_card()
        self._build_result_panel()
        self._build_info_panel()
        self._build_history_panel()

    # ── Input panel ───────────────────────────────────────────────────────────

    def _build_input_panel(self) -> None:
        t = self.t
        card = self._card(self._left, "⊕  Input")

        ctk.CTkLabel(card, text="Trigonometric Ratio",
                     font=self._lf(), text_color=t["text_sub"]
                     ).pack(anchor="w", padx=16, pady=(10, 2))

        self._ratio_var = ctk.StringVar(value="Sin")
        ctk.CTkOptionMenu(
            card, variable=self._ratio_var, values=RATIO_OPTIONS,
            font=ctk.CTkFont("Helvetica", 14, "bold"),
            fg_color=t["surface2"], button_color=t["accent"],
            button_hover_color=t["accent2"], text_color=t["text"],
            width=280, height=40,
            command=lambda _: self._on_change(),
        ).pack(padx=16, pady=(0, 10))

        ctk.CTkLabel(card, text="Angle Value",
                     font=self._lf(), text_color=t["text_sub"]
                     ).pack(anchor="w", padx=16, pady=(4, 2))

        self._angle_var = ctk.StringVar(value="30")
        self._angle_entry = ctk.CTkEntry(
            card, textvariable=self._angle_var,
            font=ctk.CTkFont("Courier", 22, "bold"),
            text_color=t["text"], fg_color=t["surface2"],
            border_color=t["accent"], border_width=2,
            width=280, height=50, justify="center",
        )
        self._angle_entry.pack(padx=16, pady=(0, 10))
        self._angle_var.trace_add("write", lambda *_: self._on_change())

        ctk.CTkLabel(card, text="Angle Unit",
                     font=self._lf(), text_color=t["text_sub"]
                     ).pack(anchor="w", padx=16, pady=(4, 4))

        self._unit_var = ctk.StringVar(value="Degrees")
        uf = ctk.CTkFrame(card, fg_color="transparent")
        uf.pack(padx=16, pady=(0, 12))
        for unit in ("Degrees", "Radians", "Gradians"):
            ctk.CTkRadioButton(
                uf, text=unit, variable=self._unit_var, value=unit,
                font=ctk.CTkFont("Helvetica", 13),
                text_color=t["text"], fg_color=t["accent"],
                hover_color=t["accent2"],
                command=self._on_change,
            ).pack(side="left", padx=6)

        bf = ctk.CTkFrame(card, fg_color="transparent")
        bf.pack(padx=16, pady=(0, 14))
        ctk.CTkButton(
            bf, text="⎘ Copy Result",
            font=ctk.CTkFont("Helvetica", 12),
            fg_color=t["surface2"], hover_color=t["accent"],
            text_color=t["text"], width=130, height=34,
            command=self._copy_result,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            bf, text="⎘ Copy All",
            font=ctk.CTkFont("Helvetica", 12),
            fg_color=t["surface2"], hover_color=t["accent2"],
            text_color=t["text"], width=130, height=34,
            command=self._copy_all,
        ).pack(side="left")

    # ── Conversion card ───────────────────────────────────────────────────────

    def _build_conversion_card(self) -> None:
        t = self.t
        card = self._card(self._left, "⟳  Angle Conversions")
        self._conv_labels: dict[str, ctk.CTkLabel] = {}

        for label, key in [("Degrees", "deg"), ("Radians", "rad"), ("Gradians", "grad")]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(row, text=f"{label}:", font=self._lf(),
                         text_color=t["text_sub"], width=80, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(row, text="—",
                               font=ctk.CTkFont("Courier", 13, "bold"),
                               text_color=t["text"], anchor="w")
            lbl.pack(side="left", padx=4)
            self._conv_labels[key] = lbl

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    # ── Advanced card (collapsible) ───────────────────────────────────────────

    def _build_advanced_card(self) -> None:
        t = self.t
        outer = ctk.CTkFrame(self._left, fg_color=t["surface"], corner_radius=12)
        outer.pack(fill="x", pady=(0, 10))

        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(10, 6))

        self._adv_toggle_lbl = ctk.CTkLabel(
            hdr, text="▶  Advanced",
            font=ctk.CTkFont("Helvetica", 13, "bold"),
            text_color=t["accent"], cursor="hand2",
        )
        self._adv_toggle_lbl.pack(side="left")
        self._adv_toggle_lbl.bind("<Button-1>", lambda _: self._toggle_advanced())

        self._adv_body = ctk.CTkFrame(outer, fg_color="transparent")

        for label, attr in [
            ("Exact Value:", "_lbl_exact"),
            ("Period:", "_lbl_period"),
            ("Unit Circle:", "_lbl_unit_circle"),
        ]:
            row = ctk.CTkFrame(self._adv_body, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=label, font=self._lf(),
                         text_color=t["text_sub"], width=96, anchor="w").pack(side="left")
            is_exact = "Exact" in label
            font = ctk.CTkFont("Georgia", 13, slant="italic") if is_exact else ctk.CTkFont("Helvetica", 13)
            color = t["accent3"] if is_exact else t["text"]
            lbl = ctk.CTkLabel(row, text="—", font=font, text_color=color, anchor="w")
            lbl.pack(side="left", padx=4)
            setattr(self, attr, lbl)

        ctk.CTkFrame(self._adv_body, fg_color="transparent", height=8).pack()

    # ── Result panel ──────────────────────────────────────────────────────────

    def _build_result_panel(self) -> None:
        t = self.t
        card = ctk.CTkFrame(self._right, fg_color=t["surface"], corner_radius=14)
        card.pack(fill="x", pady=(0, 8))

        self._lbl_result_expr = ctk.CTkLabel(
            card, text="sin(30°)",
            font=ctk.CTkFont("Georgia", 18),
            text_color=t["text_sub"],
        )
        self._lbl_result_expr.pack(pady=(18, 2))

        self._lbl_result_value = ctk.CTkLabel(
            card, text="0.500000000000",
            font=ctk.CTkFont("Courier", 34, "bold"),
            text_color=t["accent"],
        )
        self._lbl_result_value.pack(pady=(0, 4))

        self._lbl_exact_inline = ctk.CTkLabel(
            card, text="Exact: 1/2",
            font=ctk.CTkFont("Georgia", 13, slant="italic"),
            text_color=t["accent3"],
        )
        self._lbl_exact_inline.pack(pady=(0, 14))

    # ── Info panel ────────────────────────────────────────────────────────────

    def _build_info_panel(self) -> None:
        t = self.t
        card = ctk.CTkFrame(self._right, fg_color=t["surface"], corner_radius=14)
        card.pack(fill="both", expand=True, pady=(0, 8))

        ctk.CTkLabel(card, text="ℹ  Additional Information",
                     font=ctk.CTkFont("Helvetica", 13, "bold"),
                     text_color=t["accent"]).pack(anchor="w", padx=16, pady=(10, 6))

        cols = ctk.CTkFrame(card, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        left_sub = ctk.CTkFrame(cols, fg_color=t["surface2"], corner_radius=10)
        left_sub.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self._lbl_quadrant  = self._info_row(left_sub, "Quadrant",        "—")
        self._lbl_astc      = self._info_row(left_sub, "ASTC Rule",       "—")
        self._lbl_ref_deg   = self._info_row(left_sub, "Ref Angle (°)",   "—")
        self._lbl_ref_rad   = self._info_row(left_sub, "Ref Angle (rad)", "—")
        self._lbl_ref_grad  = self._info_row(left_sub, "Ref Angle (gon)", "—")
        ctk.CTkFrame(left_sub, fg_color="transparent", height=6).pack()

        right_sub = ctk.CTkFrame(cols, fg_color=t["surface2"], corner_radius=10)
        right_sub.pack(side="left", fill="both", expand=True, padx=(4, 0))

        ctk.CTkLabel(right_sub, text="Sign Analysis",
                     font=ctk.CTkFont("Helvetica", 12, "bold"),
                     text_color=t["text_sub"]).pack(pady=(10, 4))

        self._sign_labels: dict[str, ctk.CTkLabel] = {}
        for ratio in RATIO_OPTIONS:
            row = ctk.CTkFrame(right_sub, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(row, text=f"{ratio}:", font=self._lf(),
                         text_color=t["text_sub"], width=56, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(row, text="—",
                               font=ctk.CTkFont("Helvetica", 12, "bold"),
                               text_color=t["text"], anchor="w")
            lbl.pack(side="left")
            self._sign_labels[ratio] = lbl
        ctk.CTkFrame(right_sub, fg_color="transparent", height=6).pack()

    # ── History panel ─────────────────────────────────────────────────────────

    def _build_history_panel(self) -> None:
        t = self.t
        outer = ctk.CTkFrame(self._right, fg_color=t["surface"], corner_radius=12)
        outer.pack(fill="x")

        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(10, 0))

        ctk.CTkLabel(hdr, text="⏱  History",
                     font=ctk.CTkFont("Helvetica", 13, "bold"),
                     text_color=t["accent"]).pack(side="left")

        ctk.CTkButton(
            hdr, text="⬇ CSV", width=70, height=28,
            font=ctk.CTkFont("Helvetica", 11),
            fg_color=t["surface2"], hover_color=t["accent3"],
            text_color=t["text"], command=self._export_csv,
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            hdr, text="✕ Clear", width=70, height=28,
            font=ctk.CTkFont("Helvetica", 11),
            fg_color=t["surface2"], hover_color=t["error"],
            text_color=t["text"], command=self._clear_history,
        ).pack(side="right")

        self._hist_search_var = ctk.StringVar()
        self._hist_search_var.trace_add("write", lambda *_: self._refresh_history_ui())
        ctk.CTkEntry(
            outer, textvariable=self._hist_search_var,
            placeholder_text="Search history…",
            font=ctk.CTkFont("Helvetica", 12),
            fg_color=t["surface2"], border_color=t["border"],
            text_color=t["text"], height=32,
        ).pack(fill="x", padx=12, pady=(8, 0))

        self._hist_list = ctk.CTkScrollableFrame(
            outer, fg_color=t["bg"], height=130,
            scrollbar_button_color=t["border"], corner_radius=8,
        )
        self._hist_list.pack(fill="x", padx=12, pady=(6, 12))
        self._hist_item_frames: list[ctk.CTkFrame] = []

    # ─────────────────────────────────────────────────────────────────────────
    # EVENTS
    # ─────────────────────────────────────────────────────────────────────────

    def _on_change(self, *_) -> None:
        raw = self._angle_var.get().strip()
        if not raw:
            self._show_placeholder(); return
        try:
            value = float(raw)
        except ValueError:
            self._show_error("Invalid input"); return

        result = compute(self._ratio_var.get(), value, self._unit_var.get())
        self._last_result = result

        self._update_result_panel(result)
        self._update_conversion_card(result)
        self._update_info_panel(result)
        self._update_advanced(result)
        self._history.push(result)
        self._refresh_history_ui()

    def _on_theme_change(self, name: str) -> None:
        self._theme_name = name
        # Destroy and rebuild entire UI with new theme
        for widget in self.winfo_children():
            widget.destroy()
        self._apply_ctk_mode()
        self._hist_item_frames = []
        self._advanced_open = False
        self._build_ui()
        # Restore state
        self._ratio_var.set(self._ratio_var.get() if hasattr(self, '_ratio_var') else "Sin")
        self._on_change()

    def _toggle_advanced(self) -> None:
        self._advanced_open = not self._advanced_open
        if self._advanced_open:
            self._adv_toggle_lbl.configure(text="▼  Advanced")
            self._adv_body.pack(fill="x", padx=8)
        else:
            self._adv_toggle_lbl.configure(text="▶  Advanced")
            self._adv_body.pack_forget()

    def _copy_result(self) -> None:
        if self._last_result:
            self.clipboard_clear()
            self.clipboard_append(self._last_result.value)

    def _copy_all(self) -> None:
        if not self._last_result:
            return
        r = self._last_result
        lines = [
            f"Ratio    : {r.ratio}",
            f"Angle    : {r.degrees:.10g}°",
            f"Radians  : {r.radians:.10f}",
            f"Gradians : {r.gradians:.10f}",
            f"Value    : {r.value}",
        ]
        if r.exact_value:
            lines.append(f"Exact    : {r.exact_value}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))

    def _clear_history(self) -> None:
        self._history.clear()
        self._refresh_history_ui()

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export History",
        )
        if path:
            self._history.export_csv(path)
            messagebox.showinfo("Exported", f"History saved to:\n{path}")

    # ─────────────────────────────────────────────────────────────────────────
    # UPDATERS
    # ─────────────────────────────────────────────────────────────────────────

    def _update_result_panel(self, r: TrigResult) -> None:
        t = self.t
        self._lbl_result_expr.configure(
            text=f"{r.ratio.lower()}({r.degrees:.8g}°)")
        is_undef = r.value == "Undefined"
        self._lbl_result_value.configure(
            text=r.value,
            text_color=t["undefined"] if is_undef else t["accent"])
        if r.exact_value and not is_undef:
            self._lbl_exact_inline.configure(
                text=f"Exact: {r.exact_value}", text_color=t["accent3"])
        else:
            self._lbl_exact_inline.configure(text="")

    def _update_conversion_card(self, r: TrigResult) -> None:
        self._conv_labels["deg"].configure(text=f"{r.degrees:.8f}°")
        self._conv_labels["rad"].configure(text=f"{r.radians:.8f} rad")
        self._conv_labels["grad"].configure(text=f"{r.gradians:.8f} gon")

    def _update_info_panel(self, r: TrigResult) -> None:
        t = self.t
        self._lbl_quadrant.configure(text=quadrant_label(r.quadrant))
        self._lbl_astc.configure(text=astc_label(r.quadrant))
        self._lbl_ref_deg.configure(text=f"{r.reference_deg:.8f}°")
        self._lbl_ref_rad.configure(text=f"{r.reference_rad:.8f}")
        self._lbl_ref_grad.configure(text=f"{r.reference_grad:.8f}")

        sign_colours = {
            "Positive": t["success"],
            "Negative": t["error"],
            "Axis":     t["warning"],
        }
        for ratio, sign in r.sign_map.items():
            self._sign_labels[ratio].configure(
                text=sign, text_color=sign_colours.get(sign, t["text"]))

    def _update_advanced(self, r: TrigResult) -> None:
        self._lbl_exact.configure(
            text=r.exact_value if r.exact_value else "Not a standard angle")
        self._lbl_period.configure(
            text=f"{r.period_deg}°  ({deg_to_rad(r.period_deg):.6f} rad)")
        self._lbl_unit_circle.configure(
            text=f"{r.normalised_deg:.6g}°  (normalised)")

    def _show_placeholder(self) -> None:
        self._lbl_result_value.configure(text="—", text_color=self.t["text_dim"])
        self._lbl_result_expr.configure(text="Enter an angle above")
        self._lbl_exact_inline.configure(text="")

    def _show_error(self, msg: str) -> None:
        self._lbl_result_value.configure(text=msg, text_color=self.t["error"])
        self._lbl_result_expr.configure(text="")
        self._lbl_exact_inline.configure(text="")

    def _refresh_history_ui(self) -> None:
        t = self.t
        for f in self._hist_item_frames:
            f.destroy()
        self._hist_item_frames.clear()

        for entry in self._history.search(self._hist_search_var.get()):
            frm = ctk.CTkFrame(self._hist_list, fg_color=t["surface"], corner_radius=6)
            frm.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(frm, text=entry.short_label(),
                         font=ctk.CTkFont("Courier", 12),
                         text_color=t["text"], anchor="w"
                         ).pack(side="left", padx=8, pady=4)
            ctk.CTkLabel(frm, text=entry.timestamp,
                         font=ctk.CTkFont("Helvetica", 10),
                         text_color=t["text_dim"]
                         ).pack(side="right", padx=8)
            self._hist_item_frames.append(frm)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _card(self, parent, title: str) -> ctk.CTkFrame:
        t = self.t
        outer = ctk.CTkFrame(parent, fg_color=t["surface"], corner_radius=12)
        outer.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(outer, text=title,
                     font=ctk.CTkFont("Helvetica", 13, "bold"),
                     text_color=t["accent"]).pack(anchor="w", padx=16, pady=(10, 4))
        return outer

    def _lf(self) -> ctk.CTkFont:
        return ctk.CTkFont("Helvetica", 12)

    def _info_row(self, parent, label: str, default: str) -> ctk.CTkLabel:
        t = self.t
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(row, text=f"{label}:", font=self._lf(),
                     text_color=t["text_sub"], width=112, anchor="w").pack(side="left")
        val = ctk.CTkLabel(row, text=default,
                           font=ctk.CTkFont("Courier", 12, "bold"),
                           text_color=t["text"], anchor="w")
        val.pack(side="left", padx=4)
        return val
