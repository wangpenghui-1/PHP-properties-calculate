# -*- coding: utf-8 -*-
"""
@File: php_property_calculator.py
@Author: Gemini AI Expert
@Date: 2025-09-22
@Description: A desktop application for calculating thermophysical properties
             and key dimensionless numbers for common pulsating heat pipe (PHP)
             working fluids using Python, Tkinter, and the CoolProp library.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

# 检查并尝试导入CoolProp，如果失败则提示用户安装
try:
    from CoolProp.CoolProp import PropsSI, get_fluid_param_string
except ImportError:
    messagebox.showerror(
        "缺少库",
        "核心计算库CoolProp未找到。\n请使用 'pip install coolprop' 命令进行安装。"
    )
    exit()

class PHPPropertyCalculator(tk.Tk):
    """
    脉动热管(PHP)工质物性计算器主程序
    """
    def __init__(self):
        super().__init__()
        self.title("PHP工质物性计算与查询软件")
        self.geometry("800x600")
        
        # --- 数据变量 ---
        # 调整了工质顺序，将低温工质置于列表前方
        self.fluids = [
            # Low Temperature Fluids
            'Helium', 'Nitrogen', 'Argon', 'Hydrogen', 'Methane', 'Neon', 'Oxygen',
            # Conventional Fluids
            'Acetone', 'Ethanol', 'Methanol', 'R134a', 'Water',
        ]
        self.selected_fluid = tk.StringVar(value=self.fluids[0])
        
        # 新增：计算模式变量
        self.calc_mode = tk.StringVar(value="Saturated") # "Saturated" or "Non-Saturated"
        
        self.calc_basis = tk.StringVar(value="T") # 'T' for temperature, 'P' for pressure
        
        self.temp_k = tk.StringVar() # 变量名由 temp_c 改为 temp_k
        self.press_kpa = tk.StringVar()
        self.diameter_mm = tk.StringVar()
        self.velocity_ms = tk.StringVar()

        # 新增：工质关键参数变量
        self.point_label_temp = tk.StringVar() # 动态标签: 三相点/λ点
        self.point_label_press = tk.StringVar() # 动态标签: 三相点/λ点
        self.point_val_temp = tk.StringVar()
        self.point_val_press = tk.StringVar()
        self.t_crit_k = tk.StringVar()
        self.p_crit_kpa = tk.StringVar()
        
        # --- UI布局与事件绑定 ---
        self.create_widgets()

    def create_widgets(self):
        """创建并布局所有UI控件"""
        
        # 主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建左侧的输入框架
        input_frame = ttk.LabelFrame(main_frame, text="输入参数", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # 创建右侧的输出框架
        output_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="10")
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=10)

        # --- 填充输入框架 ---
        
        # 工质选择
        ttk.Label(input_frame, text="工质:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fluid_combo = ttk.Combobox(input_frame, textvariable=self.selected_fluid, values=self.fluids, state="readonly")
        self.fluid_combo.grid(row=0, column=1, sticky=tk.EW, pady=5, columnspan=2)

        # 新增：计算模式选择
        ttk.Label(input_frame, text="计算模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sat_radio = ttk.Radiobutton(input_frame, text="饱和状态", variable=self.calc_mode, value="Saturated")
        self.nonsat_radio = ttk.Radiobutton(input_frame, text="非饱和状态", variable=self.calc_mode, value="Non-Saturated")
        self.sat_radio.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.nonsat_radio.grid(row=2, column=2, columnspan=1, sticky=tk.W)

        # 计算基准
        ttk.Label(input_frame, text="计算基准:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.temp_radio = ttk.Radiobutton(input_frame, text="按温度计算", variable=self.calc_basis, value="T")
        self.press_radio = ttk.Radiobutton(input_frame, text="按压力计算", variable=self.calc_basis, value="P")
        self.temp_radio.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.press_radio.grid(row=4, column=2, columnspan=1, sticky=tk.W)

        # 输入框
        # 标签和单位从 °C 改为 K
        ttk.Label(input_frame, text="温度 (T):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.temp_entry = ttk.Entry(input_frame, textvariable=self.temp_k)
        self.temp_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)
        ttk.Label(input_frame, text="K").grid(row=5, column=2, sticky=tk.W)

        ttk.Label(input_frame, text="压力 (P):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.press_entry = ttk.Entry(input_frame, textvariable=self.press_kpa)
        self.press_entry.grid(row=6, column=1, sticky=tk.EW, pady=5)
        ttk.Label(input_frame, text="kPa").grid(row=6, column=2, sticky=tk.W)

        ttk.Label(input_frame, text="管内径 (D):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.dia_entry = ttk.Entry(input_frame, textvariable=self.diameter_mm)
        self.dia_entry.grid(row=7, column=1, sticky=tk.EW, pady=5)
        ttk.Label(input_frame, text="mm").grid(row=7, column=2, sticky=tk.W)

        ttk.Label(input_frame, text="速度 (u):").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.vel_entry = ttk.Entry(input_frame, textvariable=self.velocity_ms)
        self.vel_entry.grid(row=8, column=1, sticky=tk.EW, pady=5)
        ttk.Label(input_frame, text="m/s").grid(row=8, column=2, sticky=tk.W)
        
        # 操作按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        self.calc_button = ttk.Button(button_frame, text="计算")
        self.calc_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="清除")
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        
        input_frame.columnconfigure(1, weight=1)

        # 新增：工质关键参数显示区
        key_params_frame = ttk.LabelFrame(input_frame, text="工质关键参数", padding="10")
        key_params_frame.grid(row=10, column=0, columnspan=3, sticky=tk.EW, pady=(10, 0))

        ttk.Label(key_params_frame, text="临界点温度 (T_crit):").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(key_params_frame, textvariable=self.t_crit_k, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(key_params_frame, text="临界点压力 (P_crit):").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(key_params_frame, textvariable=self.p_crit_kpa, font=("TkDefaultFont", 9, "bold")).grid(row=1, column=1, sticky=tk.W)

        # 标签和值都使用StringVar，以实现动态更新
        ttk.Label(key_params_frame, textvariable=self.point_label_temp).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(key_params_frame, textvariable=self.point_val_temp, font=("TkDefaultFont", 9, "bold")).grid(row=2, column=1, sticky=tk.W)

        ttk.Label(key_params_frame, textvariable=self.point_label_press).grid(row=3, column=0, sticky=tk.W)
        ttk.Label(key_params_frame, textvariable=self.point_val_press, font=("TkDefaultFont", 9, "bold")).grid(row=3, column=1, sticky=tk.W)

        # --- 填充输出框架 ---
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, state="disabled", height=25, width=60)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.output_text, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # --- 事件绑定 ---
        self.fluid_combo.bind("<<ComboboxSelected>>", self.on_fluid_select)
        self.calc_button.config(command=self.on_calculate)
        self.clear_button.config(command=self.on_clear)
        
        # 模式切换事件
        self.sat_radio.config(command=self.on_mode_change)
        self.nonsat_radio.config(command=self.on_mode_change)

        # 基准切换事件
        self.temp_radio.config(command=self.on_basis_change)
        self.press_radio.config(command=self.on_basis_change)
        
        # 绑定 <FocusOut> 事件用于自动更新T/P
        self.temp_entry.bind("<FocusOut>", self.auto_update_tp)
        self.press_entry.bind("<FocusOut>", self.auto_update_tp)

        # 初始化UI状态，确保启动时界面状态正确
        self.on_mode_change()
        # 初始化时，为默认工质加载关键参数
        self.on_fluid_select()

    def on_calculate(self):
        """
        处理“计算”按钮点击事件。
        调用核心计算函数，如果成功则将结果格式化并显示。
        """
        results = self._calculate_properties()
        if results:
            self.format_and_display_results(results)

    def on_fluid_select(self, event=None):
        """当用户选择新工质时，查询并显示其关键参数"""
        fluid = self.selected_fluid.get()
        
        # 为了调用PropsSI查询不依赖于状态的物性参数（如临界/三相点），
        # 我们需要提供一组任意但有效的状态参数作为占位符。
        # CoolProp在查询这些固定参数时会忽略这些占位符的值。
        dummy_T = 300  # K
        dummy_P = 101325  # Pa

        # 查询临界点参数
        try:
            # 修正：查询固有常数时，不需要提供状态参数
            t_crit = PropsSI('Tcrit', fluid)
            p_crit = PropsSI('Pcrit', fluid) # Pa
            self.t_crit_k.set(f"{t_crit:.2f} K")
            self.p_crit_kpa.set(f"{p_crit / 1000.0:.2f} kPa")
        except Exception as e:
            print(f"Error getting critical properties for {fluid}: {e}")
            self.t_crit_k.set("N/A")
            self.p_crit_kpa.set("N/A")
        
        # 根据工质类型，查询三相点或λ点
        if fluid == 'Helium':
            # 特殊处理氦：查询λ点。λ点参数不能通过PropsSI获取，需要调用底层函数。
            self.point_label_temp.set("λ点温度 (T_λ):")
            self.point_label_press.set("λ点压力 (P_λ):")
            try:
                # 最终修正：使用 get_fluid_param_string 获取所有流体参数的JSON，然后解析
                # 这是最可靠的方法，避免了PropsSI在不同版本/后台下的不确定性
                params_str = get_fluid_param_string(fluid, "JSON")
                params = json.loads(params_str)
                # 对于氦, CoolProp 将 lambda 点的数据存储在 "triple_liquid" 键下
                lambda_point_data = params[0]['STATES']['triple_liquid']
                t_lambda = lambda_point_data['T']
                p_lambda = lambda_point_data['p'] # 单位: Pa
                self.point_val_temp.set(f"{t_lambda:.3f} K")
                self.point_val_press.set(f"{p_lambda / 1000.0:.3f} kPa")
            except Exception as e:
                print(f"Definitive Error getting Lambda properties for Helium: {e}")
                self.point_val_temp.set("N/A")
                self.point_val_press.set("N/A")
        else:
            # 其他工质：查询三相点
            self.point_label_temp.set("三相点温度 (T_trip):")
            self.point_label_press.set("三相点压力 (P_trip):")
            try:
                # 修正：查询固有常数时，不需要提供状态参数
                t_triple = PropsSI('Ttriple', fluid)
                p_triple = PropsSI('ptriple', fluid) # Pa
                self.point_val_temp.set(f"{t_triple:.2f} K")
                self.point_val_press.set(f"{p_triple / 1000.0:.3f} kPa")
            except Exception as e:
                print(f"Error getting triple properties for {fluid}: {e}")
                self.point_val_temp.set("N/A")
                self.point_val_press.set("N/A")

    def on_clear(self):
        """处理“清除”按钮点击事件，重置所有输入输出。"""
        self.temp_k.set("")
        self.press_kpa.set("")
        self.diameter_mm.set("")
        self.velocity_ms.set("")
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
    
    def on_mode_change(self):
        """处理计算模式切换事件"""
        if self.calc_mode.get() == "Saturated":
            # 启用“计算基准”选项
            self.temp_radio.config(state="normal")
            self.press_radio.config(state="normal")
            # 根据“计算基准”更新T/P输入框状态
            self.on_basis_change()
        else: # "Non-Saturated"
            # 禁用“计算基准”选项
            self.temp_radio.config(state="disabled")
            self.press_radio.config(state="disabled")
            # T和P输入框都变为可用
            self.temp_entry.config(state="normal")
            self.press_entry.config(state="normal")

    def on_basis_change(self):
        """
        处理单选按钮切换事件。
        根据选择是“按温度”还是“按压力”，来控制对应输入框的读写状态。
        """
        if self.calc_basis.get() == "T":
            self.temp_entry.config(state="normal")
            self.press_entry.config(state="readonly")
        else:
            self.temp_entry.config(state="readonly")
            self.press_entry.config(state="normal")
            
    def auto_update_tp(self, event=None):
        """
        当在T或P输入框失去焦点时，自动计算并填充对应的饱和P或T
        """
        # 此功能仅在饱和模式下有效
        if self.calc_mode.get() != "Saturated":
            return
            
        basis = self.calc_basis.get()
        fluid = self.selected_fluid.get()
        
        try:
            # 单位逻辑已修改为K
            if basis == 'T' and self.temp_k.get():
                T_K = float(self.temp_k.get())
                P_Pa = PropsSI('P', 'T', T_K, 'Q', 0, fluid)
                self.press_kpa.set(f"{P_Pa/1000.0:.2f}")
            elif basis == 'P' and self.press_kpa.get():
                P_kPa = float(self.press_kpa.get())
                P_Pa = P_kPa * 1000.0
                T_K = PropsSI('T', 'P', P_Pa, 'Q', 0, fluid)
                self.temp_k.set(f"{T_K:.2f}")
        except Exception:
            # 如果输入无效或超出范围，CoolProp会出错，这里静默处理
            # 最终点击“计算”时会弹出详细错误
            if basis == 'T':
                self.press_kpa.set("")
            else:
                self.temp_k.set("")

    def format_and_display_results(self, results):
        """格式化计算结果并将其显示在输出文本区域"""
        
        # 根据返回的模式，选择不同的格式化方案
        if results.get("mode") == "Saturated":
            output_string = self._format_saturated_results(results)
        elif results.get("mode") == "Non-Saturated":
            output_string = self._format_nonsaturated_results(results)
        else:
            output_string = "发生未知错误：无法格式化结果。"

        # 更新UI
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output_string)
        self.output_text.config(state="disabled")

    def _format_saturated_results(self, results):
        """格式化饱和状态的计算结果"""
        inputs = results["inputs"]
        liquid = results["liquid_props"]
        vapor = results["vapor_props"]
        phase_change = results["phase_change_props"]
        dimensionless = results["dimensionless_numbers"]
        
        return (
            f"--- 计算结果 (工质: {inputs['fluid']} @ {inputs['T_K']:.2f} K / {inputs['P_kPa']:.1f} kPa) ---\n"
            f"状态: 饱和状态\n\n"
            f"**[液相物性]**\n"
            f"- 密度 (ρ_l): {liquid['rho_l']:.2f} kg/m³\n"
            f"- 动力粘度 (μ_l): {liquid['mu_l']:.4E} Pa·s\n"
            f"- 比热容 (c_p,l): {liquid['cp_l']:.1f} J/kg·K\n"
            f"- 导热系数 (k_l): {liquid['k_l']:.4f} W/m·K\n"
            f"- 表面张力 (σ): {liquid['sigma']:.4E} N/m\n\n"
            f"**[气相物性]**\n"
            f"- 密度 (ρ_v): {vapor['rho_v']:.3f} kg/m³\n"
            f"- 动力粘度 (μ_v): {vapor['mu_v']:.4E} Pa·s\n\n"
            f"**[相变物性]**\n"
            f"- 汽化潜热 (h_fg): {phase_change['h_fg']:.4E} J/kg\n\n"
            f"**[关键无量纲数]**\n"
            f"- 雷诺数 (Re_l): {dimensionless['Re_l']:.1f}\n"
            f"- 普朗特数 (Pr_l): {dimensionless['Pr_l']:.2f}\n"
            f"- 邦德数 (Bo): {dimensionless['Bo']:.2f}\n"
            f"- 韦伯数 (We_l): {dimensionless['We_l']:.2f}\n"
            f"---"
        )
        
    def _format_nonsaturated_results(self, results):
        """格式化非饱和状态的计算结果"""
        inputs = results["inputs"]
        props = results["properties"]
        dimensionless = results["dimensionless_numbers"]
        
        # 将英文状态翻译为中文
        phase_translation = {
            "Subcooled Liquid": "过冷液体",
            "Superheated Vapor": "过热蒸汽"
        }
        phase_str = phase_translation.get(results['phase'], results['phase'])

        return (
            f"--- 计算结果 (工质: {inputs['fluid']} @ {inputs['T_K']:.2f} K / {inputs['P_kPa']:.1f} kPa) ---\n"
            f"状态: {phase_str}\n\n"
            f"**[物性]**\n"
            f"- 密度 (ρ): {props['rho']:.3f} kg/m³\n"
            f"- 动力粘度 (μ): {props['mu']:.4E} Pa·s\n"
            f"- 比热容 (c_p): {props['cp']:.1f} J/kg·K\n"
            f"- 导热系数 (k): {props['k']:.3f} W/m·K\n\n"
            f"**[关键无量纲数]**\n"
            f"- 雷诺数 (Re): {dimensionless['Re']:.1f}\n"
            f"- 普朗特数 (Pr): {dimensionless['Pr']:.2f}\n"
            f"---"
        )

    def _calculate_properties(self):
        """
        核心计算函数，根据选择的模式（饱和/非饱和）进行计算。
        所有计算都在try-except块中进行以捕获潜在错误。
        """
        try:
            # --- 1. 获取通用输入 ---
            fluid = self.selected_fluid.get()
            D_m = float(self.diameter_mm.get()) / 1000.0  # mm -> m
            u_ms = float(self.velocity_ms.get())

            # --- 2. 根据模式进行分支计算 ---
            if self.calc_mode.get() == "Saturated":
                return self._calculate_saturated_properties(fluid, D_m, u_ms)
            else: # "Non-Saturated"
                return self._calculate_nonsaturated_properties(fluid, D_m, u_ms)

        except Exception as e:
            messagebox.showerror("计算错误", f"发生错误: {e}\n\n请检查输入值是否有效或在工质范围内。")
            return None

    def _calculate_saturated_properties(self, fluid, D_m, u_ms):
        """计算饱和状态下的物性"""
        # --- 2a. 根据计算基准，确定饱和状态点 (T, P) ---
        if self.calc_basis.get() == "T":
            T_K = float(self.temp_k.get())
            P_Pa = PropsSI('P', 'T', T_K, 'Q', 0, fluid)
            P_kPa = P_Pa / 1000.0
            self.press_kpa.set(f"{P_kPa:.2f}")
        else: # self.calc_basis.get() == "P"
            P_kPa = float(self.press_kpa.get())
            P_Pa = P_kPa * 1000.0
            T_K = PropsSI('T', 'P', P_Pa, 'Q', 0, fluid)
            self.temp_k.set(f"{T_K:.2f}")
        
        # --- 3a. 查询饱和物性 ---
        rho_l = PropsSI('D', 'T', T_K, 'Q', 0, fluid)
        mu_l = PropsSI('V', 'T', T_K, 'Q', 0, fluid)
        cp_l = PropsSI('C', 'T', T_K, 'Q', 0, fluid)
        k_l = PropsSI('L', 'T', T_K, 'Q', 0, fluid)
        sigma = PropsSI('I', 'T', T_K, 'Q', 0, fluid)
        rho_v = PropsSI('D', 'T', T_K, 'Q', 1, fluid)
        mu_v = PropsSI('V', 'T', T_K, 'Q', 1, fluid)
        h_l = PropsSI('H', 'T', T_K, 'Q', 0, fluid)
        h_v = PropsSI('H', 'T', T_K, 'Q', 1, fluid)
        h_fg = h_v - h_l

        # --- 4a. 计算无量纲数 (饱和) ---
        g = 9.81
        Re_l = (rho_l * u_ms * D_m) / mu_l if mu_l != 0 else 0
        Pr_l = (cp_l * mu_l) / k_l if k_l != 0 else 0
        Bo = (g * (rho_l - rho_v) * D_m**2) / sigma if sigma != 0 else 0
        We_l = (rho_l * u_ms**2 * D_m) / sigma if sigma != 0 else 0

        # --- 5a. 返回结果字典 ---
        return {
            "mode": "Saturated",
            "inputs": {"fluid": fluid, "T_K": T_K, "P_kPa": P_kPa},
            "liquid_props": {"rho_l": rho_l, "mu_l": mu_l, "cp_l": cp_l, "k_l": k_l, "sigma": sigma},
            "vapor_props": {"rho_v": rho_v, "mu_v": mu_v},
            "phase_change_props": {"h_fg": h_fg},
            "dimensionless_numbers": {"Re_l": Re_l, "Pr_l": Pr_l, "Bo": Bo, "We_l": We_l}
        }

    def _calculate_nonsaturated_properties(self, fluid, D_m, u_ms):
        """计算非饱和状态下的物性"""
        # --- 2b. 获取非饱和状态点 (T, P) ---
        T_K = float(self.temp_k.get())
        P_kPa = float(self.press_kpa.get())
        P_Pa = P_kPa * 1000.0

        # --- 3b. 判断物相 ---
        T_sat = PropsSI('T', 'P', P_Pa, 'Q', 0, fluid) # 该压力下的饱和温度
        if T_K < T_sat:
            phase = "Subcooled Liquid"
        else:
            phase = "Superheated Vapor"
            
        # --- 4b. 查询单相物性 ---
        rho = PropsSI('D', 'T', T_K, 'P', P_Pa, fluid)
        mu = PropsSI('V', 'T', T_K, 'P', P_Pa, fluid)
        cp = PropsSI('C', 'T', T_K, 'P', P_Pa, fluid)
        k = PropsSI('L', 'T', T_K, 'P', P_Pa, fluid)

        # --- 5b. 计算无量纲数 (非饱和) ---
        Re = (rho * u_ms * D_m) / mu if mu != 0 else 0
        Pr = (cp * mu) / k if k != 0 else 0
        
        # --- 6b. 返回结果字典 ---
        return {
            "mode": "Non-Saturated",
            "inputs": {"fluid": fluid, "T_K": T_K, "P_kPa": P_kPa},
            "phase": phase,
            "properties": {"rho": rho, "mu": mu, "cp": cp, "k": k},
            "dimensionless_numbers": {"Re": Re, "Pr": Pr}
        }
        
if __name__ == "__main__":
    app = PHPPropertyCalculator()
    app.mainloop()
