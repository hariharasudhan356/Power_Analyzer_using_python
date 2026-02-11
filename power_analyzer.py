import numpy as np
import matplotlib.pyplot as plt
import math

def calculate_power(V_rms, I_rms, pf, freq=50):
    """Calculate AC power quantities and required PF correction"""
    if pf <= 0 or pf > 1:
        raise ValueError("Power factor must be between 0 and 1 (exclusive of 0)")
    
    S = V_rms * I_rms                  # Apparent power (VA)
    P = S * pf                        # Active power (W)
    Q = S * math.sqrt(1 - pf**2)      # Reactive power (VAR)
    theta = math.acos(pf)             # Phase angle in radians
    theta_deg = math.degrees(theta)
    
    # Calculate Capacitor for PF Correction (Targeting 0.95)
    target_pf = 0.95
    c_microfarad = 0
    if pf < target_pf and P > 0:
        phi1 = theta
        phi2 = math.acos(target_pf)
        # Standard EEE Capacitance formula: C = P(tanθ1 - tanθ2) / (2πfV²)
        C = (P * (math.tan(phi1) - math.tan(phi2))) / (2 * math.pi * freq * V_rms**2)
        c_microfarad = C * 1e6 # Convert to microFarads

    return {
        'S': round(S, 2),
        'P': round(P, 2),
        'Q': round(Q, 2) if pf < 1 else 0,
        'theta_deg': round(theta_deg, 2),
        'pf': pf,
        'required_C': round(c_microfarad, 2)
    }

def plot_waveforms(V_rms, I_rms, pf, freq=50, cycles=3):
    """Plot voltage & current waveforms + scaled phasor diagram"""
    t = np.linspace(0, cycles/freq, 1000)
    omega = 2 * np.pi * freq
    
    theta = math.acos(pf)
    v = V_rms * np.sqrt(2) * np.sin(omega * t)
    i = I_rms * np.sqrt(2) * np.sin(omega * t - theta)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9))
    
    # --- Subplot 1: Waveforms ---
    ax1.plot(t*1000, v, label='Voltage (V)', color='blue', linewidth=2)
    ax1.plot(t*1000, i, label='Current (A)', color='red', linewidth=2)
    ax1.set_title(f'AC Waveforms ({freq}Hz)', fontsize=14)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')
    
    # --- Subplot 2: Scaled Phasor Diagram ---
    # Normalizing Current vector length to be 70% of Voltage length for visibility
    # This ensures that even if I=5A and V=230V, both arrows are clearly seen.
    v_len = V_rms
    scale_factor = (v_len / I_rms) * 0.7 
    
    # Voltage Reference (at 0 degrees)
    ax2.quiver(0, 0, v_len, 0, angles='xy', scale_units='xy', scale=1, 
               color='blue', label=f'Voltage: {V_rms}V', width=0.015)
    
    # Current Vector (Lagging by theta)
    curr_x = (I_rms * math.cos(theta)) * scale_factor
    curr_y = (I_rms * math.sin(-theta)) * scale_factor
    
    ax2.quiver(0, 0, curr_x, curr_y, angles='xy', scale_units='xy', scale=1, 
               color='red', label=f'Current (Scaled x{round(scale_factor, 1)}): {I_rms}A', width=0.01)
    
    # Formatting the Phasor Plot
    limit = v_len * 1.3
    ax2.set_xlim(-limit, limit)
    ax2.set_ylim(-limit, limit)
    ax2.set_aspect('equal')
    ax2.set_title('Phasor Diagram (Scaled for Visibility)', fontsize=14)
    ax2.axhline(0, color='black', lw=1)
    ax2.axvline(0, color='black', lw=1)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize='small')
    
    plt.tight_layout()
    plt.show()

# ---------------- Main Program ----------------
print("="*50)
print("Single-Phase AC Power Analyzer (SKCT EEE Project)")
print("="*50)

try:
    # User Inputs
    V = float(input("Enter RMS Voltage (V) [e.g. 230]: "))
    I = float(input("Enter RMS Current (A) [e.g. 5]: "))
    pf = float(input("Enter Power Factor (0.1 to 1.0) [e.g. 0.8]: "))
    f = float(input("Enter Frequency (Hz) [Enter for 50]: ") or 50)

    results = calculate_power(V, I, pf, f)
    
    print("\n" + "*"*20 + " RESULTS " + "*"*20)
    print(f"Apparent Power (S)   : {results['S']} VA")
    print(f"Active Power (P)     : {results['P']} W")
    print(f"Reactive Power (Q)   : {results['Q']} VAR")
    print(f"Phase Angle (θ)      : {results['theta_deg']}° (Lagging)")
    print(f"Power Factor (cosθ)  : {results['pf']}")
    
    if results['required_C'] > 0:
        print("\n" + "!"*5 + " PF CORRECTION SUGGESTION " + "!"*5)
        print(f"Target Power Factor : 0.95")
        print(f"Required Capacitor  : {results['required_C']} µF")
    else:
        print("\nPower factor is optimal. No correction needed.")
    print("*"*49)

    # Launch Visualizations
    plot_waveforms(V, I, pf, f)
    
except ValueError as e:
    print(f"\n[Error]: Invalid numerical input. {e}")
except Exception as e:
    print(f"\n[Error]: An unexpected issue occurred: {e}")