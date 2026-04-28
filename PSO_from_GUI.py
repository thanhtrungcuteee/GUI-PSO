

import re
import os
import time
import threading
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import qmc
from pyswarms.single.global_best import GlobalBestPSO

# Global flag for cancellation
_pso_cancelled = False

def cancel_pso():
    """Hàm để đặt flag hủy PSO"""
    global _pso_cancelled
    _pso_cancelled = True

def reset_pso_flag():
    """Reset flag hủy PSO"""
    global _pso_cancelled
    _pso_cancelled = False

try:
    import psse35         
    import psspy
    from dyntools import CHNF
    PSSE_OK = True
except ImportError:
    PSSE_OK = False
_GUI_TO_CHANNEL = {
    "P":  ["POWR", "ACTIVE POWER"],
    "Q":  ["VARS","REACTIVE POWER"],
    "Vt": ["ETRM","GENERATOR VOLTAGE"],
    "Ef": ["EFD", "FIELD VOLTAGE"],
    "If": ["XADIFD","FIELD CURRENT"]
}

def _channel_pattern(channel_key: str, bus_id: str, gen_id: str) -> str:
    if channel_key in ("FREQ", "VOLT"):
        return rf"^{channel_key}\s*{bus_id}\s*\[.*\]$"
    # elif channel_key in ("ETRM", "EFD", "XADIFD"):
    #     return rf"^{channel_key}\s+BUS\s+{bus_id}\s+MACHINE\s+'{gen_id}\s*'$"
    else:
        return rf"^{channel_key}\s*{bus_id}\[.*\]{gen_id}$"




def _init_PSSE(paths: dict, psse_setting: dict) -> None:
    sav_file = paths["sav_file"]
    dyr_file = paths["dyr_file"]
    delt     = float(psse_setting.get("delt", 0.01))

    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()

    psspy.psseinit()
    psspy.case(sav_file)
    psspy.fdns([0, 0, 0, 1, 1, 0, 99, 0])
    psspy.cong(0)

    psspy.conl(0, 1, 1, [0, 0], [100.0, 0.0, 0.0, 100.0])
    psspy.conl(0, 1, 2, [0, 0], [100.0, 0.0, 0.0, 100.0])
    psspy.conl(0, 1, 3, [0, 0], [100.0, 0.0, 0.0, 100.0])

    psspy.dyre_new([1, 1, 1, 1], dyr_file)
    psspy.ordr(0)
    psspy.fact()
    psspy.tysl(0)

    psspy.delete_all_plot_channels()
    psspy.chsb(0, 1, [-1, -1, -1, 1, 2, 0])   # POWR  — P
    psspy.chsb(0, 1, [-1, -1, -1, 1, 3, 0])   # VARS  — Q
    psspy.chsb(0, 1, [-1, -1, -1, 1, 4, 0])   # ETRM  — Vt
    psspy.chsb(0, 1, [-1, -1, -1, 1, 5, 0])   # EFD   — Ef
    psspy.chsb(0, 1, [-1, -1, -1, 1, 8, 0])   # XADIFD— If

    psspy.dynamics_solution_param_2(
        [_i, _i, _i, _i, _i, _i, _i, _i],
        [_f, _f, delt, _f, _f, _f, _f, _f]
    )
    psspy.set_zsorce_reconcile_flag(1)
    psspy.set_relang(1, 11, r"""1""")
    psspy.set_chnfil_type(0)
    psspy.set_netfrq(0)
    # psspy.progress_output(1)
    psspy.progress_output(6, "", 0)
    psspy.alert_output(6, "", 0)
    psspy.report_output(6, "", 0)
def _change_param(param_dict: dict, var_spec: list, psse_setting: dict) -> None:
    """
    param_dict : {param_name: value}
    var_spec   : list of {param_name, model_name, idx}
    """
    bus_id = int(psse_setting["bus_id"])
    gen_id = str(psse_setting["gen_id"])

    for spec in var_spec:
        name  = spec["param_name"]
        val   = float(param_dict[name])
        psspy.change_plmod_con(bus_id, gen_id, spec["model_name"], spec["idx"], val)
def _run_PSSE(paths: dict, psse_setting: dict, disturbance: str,
              targets: list) -> dict[str, pd.DataFrame]:
    out_file   = paths["out_file"]
    bus_id     = str(psse_setting["bus_id"])
    gen_id     = str(psse_setting["gen_id"]).strip()
    sim_time   = float(psse_setting.get("sim_time", 10))
    fault_time = float(psse_setting.get("fault_time", 2))

    if disturbance == "No load":
        psspy.estr_open_circuit_test(int(bus_id), float(0.02), out_file)
        psspy.erun(8, 0, 0, 0)
    elif disturbance == "step respone":
        psspy.strt_2([0, 0], out_file)
        psspy.run(0, fault_time, 0, 0, 0)
        psspy.increment_vref(int(bus_id), r"""1""", 0.03)
        psspy.run(0, sim_time, 0, 0, 0)
    elif disturbance == "impulse":
        psspy.strt_2([0, 0], out_file)
        psspy.run(0, fault_time, 0, 0, 0)
        psspy.increment_vref(int(bus_id), r"""1""", 0.05)
        psspy.run(0, fault_time + 0.1, 0, 0, 0)
        psspy.increment_vref(int(bus_id), r"""1""", -0.05)
        psspy.run(0, sim_time, 0, 0, 0)
    chnf = CHNF(out_file)
    _, chan_id_dict, chan_data_dict = chnf.get_data()
    time_data = np.array(chan_data_dict["time"])

    df_sim = {}
    for target in targets:
        channel_key = _GUI_TO_CHANNEL.get(target)[0]
        if channel_key is None:
            raise KeyError(f"Không nhận diện target '{target}'")

        pattern    = _channel_pattern(channel_key, bus_id, gen_id)
        select_id  = None
        for cid, desc in chan_id_dict.items():
            if re.match(pattern, desc.strip(), re.IGNORECASE):
                # print(f"tim thay {desc}")
                select_id = cid
                break

        if select_id is None:
            raise RuntimeError(
                f"Không tìm thấy channel '{channel_key}' (target='{target}'). "
                f"Pattern: {pattern}"
            )

        values = np.array(chan_data_dict[select_id])
        if target == "P":
            values = values * 100 /665
        elif target == "Q": 
            values = values * 100 / 412
        df     = pd.DataFrame({"Time": time_data, "Value": values})
        df_sim[target] = df.iloc[3:1003].reset_index(drop=True)


    return df_sim

def _read_ref_csv(paths: dict, targets: list, disturbance) -> dict[str, pd.DataFrame]:
    ref_file = paths["ref_file"]
    df_ref = {}
    df = pd.read_csv(ref_file)
    max_row = df.shape[0]
    max_col = df.shape[1]
    for i in range(max_row):
        for j in range(max_col):
            c1 = df.iloc[i,j]
            if c1 == "Correction cycle(s)":
                timestep = float(df.iloc[i,j+1])
            for target in targets:
                channel_key = _GUI_TO_CHANNEL.get(target)[1]
                if channel_key is None :
                    raise KeyError(f" khong co {channel_key} trong CHANNEL")
                if c1 == channel_key:
                    print(f"Da tim thay channel {channel_key}")
                    value = df.iloc[i+7:, j].astype(float).values
                    time_ref = df.iloc[10:, 0].astype(float).values * timestep
                    df_ref[target] = pd.DataFrame({"Time": time_ref, "Value": value })
                    if disturbance == "Step respone" or disturbance == "impulse":
                        df_ref[target] = df_ref[target].iloc[0:1000].reset_index(drop=True)
                    elif disturbance == "No load":
                        df_ref[target] = df_ref[target].iloc[200:1000].reset_index(drop=True)
    if disturbance == "No load":
        df_ref[target]["Time"] = df_ref[target]["Time"]- 2
    

    return df_ref
def _deviation(df_ref: dict, df_sim: dict, targets) -> float:
    total = 0.0
    for target in targets:
        # SỬA: đổi tên biến cục bộ để tránh ghi đè dict df_ref / df_sim
        ref_vals = df_ref[target].iloc[:]["Value"].values
        sim_vals = df_sim[target].iloc[:]["Value"].values
        if len(ref_vals) != len(sim_vals):
            raise ValueError(f"Kiem tra lai doc ref {len(ref_vals)} khac {len(sim_vals)}")
        sse = np.sum((ref_vals - sim_vals) ** 2)
        total += sse
    return total
def _build_var_list(input_data: dict) -> tuple[list, np.ndarray, np.ndarray, np.ndarray]:
    var_spec    = []
    warm_start  = []
    lb_list     = []
    ub_list     = []

    for key in ("gen_model", "avr_model", "gov_model", "pss_model"):
        if key not in input_data:
            continue
        info       = input_data[key]
        model_name = info["model"]
        for p_name, p_info in info["parameters"].items():
            var_spec.append({
                "param_name": p_name,
                "model_name": model_name,
                "idx":        int(p_info["idx"]),
            })
            warm_start.append(float(p_info["init"]))
            lb_list.append(float(p_info["min"]))
            ub_list.append(float(p_info["max"]))

    if not var_spec:
        raise ValueError("Không có tham số nào được chọn để tối ưu.")

    return var_spec, np.array(warm_start), np.array(lb_list), np.array(ub_list)
def _simulate(param_dict: dict, var_spec: list,
              paths: dict, psse_setting: dict,
              disturbance: str, targets: list) -> dict[str, pd.DataFrame]:
    _init_PSSE(paths, psse_setting)
    _change_param(param_dict, var_spec, psse_setting)
    df_sim = _run_PSSE(paths, psse_setting, disturbance, targets)
    return df_sim
def _init_particle_pos(warm_start: np.ndarray,
                       lb: np.ndarray, ub: np.ndarray,
                       n_particles: int) -> np.ndarray:
    sampler  = qmc.LatinHypercube(d=len(lb))
    init_pos = qmc.scale(sampler.random(n=n_particles), lb, ub)
    init_pos[0] = np.clip(warm_start, lb, ub)
    return init_pos
def _run_PSO(obj_func,
             lb: np.ndarray, ub: np.ndarray,
             warm_start: np.ndarray,
             pso_params: dict,
             log) -> tuple[np.ndarray, float, list]:
    global _pso_cancelled

    n_p       = int(pso_params["particles"])
    total_iter= int(pso_params["iterations"])
    c1        = float(pso_params["c1"])
    c2        = float(pso_params["c2"])
    w_max     = float(pso_params["wmax"])
    w_min     = float(pso_params["wmin"])
    w  = (w_max + w_min)/2
    n_restart   = int(pso_params.get("n_restart", 1))
    noise       = float(pso_params.get("noise", 0.05))

    # PSO đơn giản
    opt = {"c1": c1, "c2": c2, "w": w}

    n_dim      = len(lb)
    best_cost  = np.inf
    best_pos   = np.clip(warm_start, lb, ub)
    cost_history = []

    for restart in range(n_restart):
        if _pso_cancelled:
            log(f"\n!!! PSO bị hủy tại restart {restart+1}/{n_restart}")
            break

        log(f"\n{'='*55}")
        log(f"  RESTART {restart+1}/{n_restart}  |  Best SSE so far: {best_cost:.6f}")
        log(f"{'='*55}")
        start = (np.clip(warm_start, lb, ub) if restart == 0
                 else np.clip(best_pos + (ub - lb) * noise * np.random.randn(n_dim), lb, ub))
        log(f"  PSO: {total_iter} iters — vùng [{lb.min():.3f}, {ub.max():.3f}]")
        pso = GlobalBestPSO(
            n_particles = n_p,
            dimensions  = n_dim,
            options     = opt,
            bounds      = (lb, ub),
            init_pos    = _init_particle_pos(start, lb, ub, n_p)
        )
        cost, pos = pso.optimize(obj_func, iters=total_iter, verbose=False)
        if hasattr(pso, 'cost_history'):
            cost_history.extend(pso.cost_history if isinstance(pso.cost_history, list) else pso.cost_history.tolist())

        log(f"  PSO Best cost: {cost:.6f}")

        if cost < best_cost:
            log(f"  ✔ Cải thiện: {best_cost:.6f} → {cost:.6f}")
            best_cost, best_pos = cost, pos
        else:
            log(f"  ✘ Không cải thiện, giữ best: {best_cost:.6f}")

    log(f"\n  PSO kết thúc: best cost = {best_cost:.6f}")
    return best_pos, best_cost, cost_history

def _plot(df_ref: dict, df_sim: dict, title: str, save_path: str = None):
    """Vẽ đường ref vs sim cho tất cả target channel, lưu file và hiển thị."""
    n   = len(df_ref)
    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n), squeeze=False)

    for ax, target in zip(axes[:, 0], df_ref.keys()):
        ax.plot(df_ref[target]["Time"], df_ref[target]["Value"],
                label="Thực đo", color="blue", linewidth=1.5)
        ax.plot(df_sim[target]["Time"], df_sim[target]["Value"],
                label="Mô phỏng", color="orange", linestyle="--", linewidth=1.5)
        ax.set_title(f"{title} — {target}")
        ax.set_xlabel("Thời gian (s)")
        ax.set_ylabel("Giá trị (pu)")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        plt.close(fig)
    else:
        plt.close(fig)
def _save_result(result: dict, out_file: str) -> None:
    """Lưu best_params và convergence ra CSV cạnh out_file."""
    out_dir   = os.path.dirname(out_file) or "."
    base_name = os.path.splitext(os.path.basename(out_file))[0]

    pd.DataFrame([
        {"parameter": k, "optimal_value": v}
        for k, v in result["best_params"].items()
    ]).to_csv(os.path.join(out_dir, f"{base_name}_best_params.csv"), index=False)

def _plot_cost_history(cost_history: list, save_path: str = None):
    """Vẽ đồ thị cost history theo iteration."""
    if not cost_history:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    iterations = range(len(cost_history))
    ax.plot(iterations, cost_history, 'b-', linewidth=1.5, label='Best Cost')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Cost (SSE)')
    ax.set_title('PSO Convergence - Cost vs Iteration')
    ax.grid(True)
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        plt.close(fig)
    else:
        plt.close(fig)
def run_optimization(
    input_data: dict,
    log_cb=None,
    do_plot = True,
    cancel_check_cb=None,
) -> dict:
    global _pso_cancelled
    _pso_cancelled = False

    def log(msg: str):
        if log_cb:
            log_cb(msg)
        else:
            print(msg)

    def log_with_cancel_check(msg: str):
        log(msg)
        if cancel_check_cb and cancel_check_cb():
            raise KeyboardInterrupt("Người dùng hủy")

    paths        = input_data["paths"]
    psse_setting = input_data["psse_setting"]
    pso_params   = input_data["pso_params"]
    targets      = pso_params["tuning_target"]      # ["P", "Vt", "Ef", ...]
    disturbance  = pso_params.get("disturbance", "step respone")

    log("=" * 55)
    log("  KHỞI ĐỘNG TỐI ƯU PSO")
    log("=" * 55)
    log(f"  Bus: {psse_setting['bus_id']}  |  Gen: {psse_setting['gen_id']}")
    log(f"  Disturbance  : {disturbance}")
    log(f"  Target chan  : {targets}")
    log(f"  Particles    : {pso_params['particles']}")
    log(f"  Iterations   : {pso_params['iterations']}")
    log(f"  c1/c2        : {pso_params['c1']} / {pso_params['c2']}")
    log(f"  w (max→min)  : {pso_params['wmax']} → {pso_params['wmin']}")
    var_spec, warm_start, lb, ub = _build_var_list(input_data)
    n_dim    = len(var_spec)
    var_names = [s["param_name"] for s in var_spec]

    log(f"  Số tham số : {n_dim}")
    for i, s in enumerate(var_spec):
        log(f"    [{i}] {s['param_name']:12s}  model={s['model_name']}  "
            f"idx={s['idx']}  init={warm_start[i]:.4f}  "
            f"[{lb[i]:.4f}, {ub[i]:.4f}]")
    df_ref = _read_ref_csv(paths, targets, disturbance)
    log(f"  Đã load: {list(df_ref.keys())} — {len(next(iter(df_ref.values())))} điểm/kênh")

    if not PSSE_OK:
        log("\n[WARN] psspy không tìm thấy — chạy DRY-RUN (fitness = random).")

    def make_dict(p: np.ndarray) -> dict:
        return {s["param_name"]: p[i] for i, s in enumerate(var_spec)}

    def obj_PSO(X: np.ndarray) -> np.ndarray:
        if _pso_cancelled:
            return np.full(X.shape[0], 1e12)
        costs = []
        for p in X:
            try:
                if PSSE_OK:
                    df_sim = _simulate(make_dict(p), var_spec, paths,
                                       psse_setting, disturbance, targets)
                    costs.append(_deviation(df_ref, df_sim, targets))
                else:
                    costs.append(float(np.sum((p - warm_start) ** 2)) + np.random.rand() * 0.01)
            except Exception as e:
                log(f"    [WARN PSO] {e}")
                costs.append(1e9)
        return np.array(costs)
    t0 = time.time()
    best_pso, best_sse, cost_history = _run_PSO(obj_PSO, lb, ub, warm_start, pso_params, log)
    log(f"  PSO xong trong {time.time() - t0:.1f}s")
    best_params = make_dict(best_pso)
    mse_pct     = best_sse / 1000 * 100

    log(f"\n{'='*55}")
    log(f"  KẾT QUẢ TỐI ƯU — Disturbance: {disturbance}")
    log(f"{'='*55}")
    for name, val in best_params.items():
        spec = next(s for s in var_spec if s["param_name"] == name)
        log(f"    {name:12s} [{spec['model_name']}] = {val:.6f}")
    log(f"  SSE        : {best_sse:.6f}")
    log(f"  SSE%       : {mse_pct:.6f}")
    log(f"{'='*55}")
    if do_plot and cost_history:
        log("\n  Đang hiển thị đồ thị cost history...")
        try:
            out_dir   = os.path.dirname(paths["out_file"]) or "."
            cost_plot_path = os.path.join(out_dir, "cost_history.png")
            _plot_cost_history(cost_history, save_path=cost_plot_path)
            log(f"  Đã lưu cost history: {cost_plot_path}")
        except Exception as e:
            log(f"  [WARN] Vẽ cost history thất bại: {e}")


        log("\n  Đang hiển thị đồ thị so sánh REF vs SIM...")
        try:
            df_sim_final = _simulate(best_params, var_spec, paths,
                                     psse_setting, disturbance, targets)
            out_dir   = os.path.dirname(paths["out_file"]) or "."
            plot_path = os.path.join(out_dir, "result_plot.png")
            _plot(df_ref, df_sim_final,
                  title=f"Disturbance: {disturbance}",
                  save_path=plot_path)
            log(f"  Đã lưu đồ thị: {plot_path}")
        except Exception as e:
            log(f"  [WARN] Hiển thị đồ thị thất bại: {e}")