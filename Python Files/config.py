import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration
default_model = "gpt-5"
default_stream = False

# API configuration
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# File paths
system_prompt_path = r"C:\Users\Lmcoo\Downloads\Unanticipated-Fault\Instructions\Unanticipated_Fault_System_Prompt.txt"
system_prompt_no_possible_faults_listed_path = r"C:\Users\Lmcoo\Downloads\Unanticipated-Fault\Instructions\Unanticipated_Fault_System_Prompt_No_Possible_Faults_Listed.txt"
user_prompt_template_path = r"C:\Users\Lmcoo\Downloads\Unanticipated-Fault\Instructions\Unanticipated_Fault_User_Prompt_Template.txt"

possible_faults_19 = [
    "Refrigerant Leak",
    "Compressor Overheating and Shutdown",
    "Expansion Valve Stuck Open/Closed",
    "Evaporator Coil Icing or Airflow Blockage",
    "Micrometeorite Impact on Structural Panel",
    "Thermal Transfer Panel Malfunction",
    "Battery Cell Degradation or Failure",
    "Power Bus Short or Outage",
    "Overload or Automatic Shutdown",
    "Faulty Power Generation Input",
    "Inverter/Converter Overheating",
    "Uncontrolled Over-Pressurization",
    "Thermal Stress Misalignment",
    "Anchoring or Support Failure",
    "Communication Network Outage",
    "Sensor Failure or Drift",
    "Fault Control Software or Data Handling",
    "Robot Agent Malfunction",
    "Data Acquisition or Sync Error",
]

possible_faults_22 = possible_faults_19 + [
    "Sealant or Adhesive Degradation at Panel Joints",
    "Delamination Between Structural Layers",
    "Outside Panel Surface Coating Degradation",
]

possible_faults_136 = possible_faults_22 + [
  "Thermostat Setpoint Misconfigured",
  "Thermostat Hysteresis Too Narrow/Wide",
  "Thermostat Sensor Placement Error",
  "Compressor Hard Start Failure",
  "Compressor Suction Valve Leakback",
  "Compressor Short Cycling",
  "Refrigerant Overcharge",
  "Refrigerant Non-Condensables",
  "Upstream Refrigerant Restriction",
  "TXV Superheat Misadjusted",
  "Capillary Tube Partial Blockage",
  "Liquid Line Filter-Drier Saturated",
  "Oil Separator Malfunction",
  "Reversing Valve Stuck Mid-Position",
  "Condenser Fan Reduced RPM",
  "Evaporator Fan Reduced RPM",
  "Supply Duct Leak",
  "Return Duct Short-Circuit",
  "Coil Fouling",
  "Frost Control Sensor Failure",
  "Defrost Cycle Stuck",
  "Heat Exchanger Fin Damage",
  "Low Ambient Lockout Misfire",
  "Suction Line Insulation Degradation",
  "Liquid Line Flash Gas",
  "Crankcase Heater Failure",
  "Refrigerant Line Micro-crack",
  "Compressor Current Sensor Drift",
  "Condensate Drain Blockage",
  "Battery SoC Sensor Drift",
  "Battery Cell Imbalance",
  "BMS Thermal Throttling",
  "DC Bus Voltage Sag",
  "Converter Control Oscillation",
  "Inverter Gate Driver Intermittent",
  "Ground Fault Leakage",
  "DC-DC Brown-Out Recovery Bug",
  "MPPT Mis-Tracking",
  "Contact Resistance Growth",
  "Connector Fretting Corrosion",
  "EMI-Induced Misreadings",
  "Load Shedding Misconfiguration",
  "Tank Regulator Drift",
  "Tank Pickup Tube Crack",
  "Desiccant Saturation",
  "O-ring Permeation Leak",
  "Schrader Valve Weep",
  "Relief Valve Weeping",
  "Refrigerant Cross-Contamination",
  "Interior Temp Sensor Bias",
  "Panel Temp Sensor Delamination",
  "Ambient Sensor Solar Loading Error",
  "Pressure Transducer Zero Drift",
  "Flow Meter Calibration Loss",
  "Fan Tachometer Stuck",
  "IR Sensor Window Dusting",
  "Humidity Sensor Wetting Lag",
  "Clock Drift Between Subsystems",
  "ADC Reference Drift",
  "Sensor Mapping Mix-up",
  "Stale Telemetry Cache",
  "Compression/Quantization Artifacts",
  "Panel Fastener Loosening",
  "Panel-Frame Galvanic Corrosion",
  "Panel Gap Growth",
  "Bladder Micro-Leak",
  "TIM Pump-Out",
  "TIM Dry-Out",
  "MLI Compression/Bridging",
  "Aerogel Crack Network",
  "Coating Emittance Drift",
  "Radiative View-Factor Change",
  "Panel Bowing/Warpage",
  "Anchoring Creep",
  "Edge Insulator Charring",
  "Structural Modal Shift",
  "Fault Threshold Mis-tuned",
  "Priority Inversion in Rules",
  "Deadband Units Mismatch",
  "Unit Conversion Error",
  "Time Sync Skew",
  "Mode Latch Not Clearing",
  "Watchdog Reset Loop",
  "Telemetry Packet Loss Burst",
  "Configuration Drift",
  "Logging Level Too Low",
  "Safety Interlock Latent Trip",
  "Control Task Overrun",
  "Maintenance Panel Left Ajar",
  "Cover Left on Heat Exchanger",
  "Filter Not Re-seated",
  "Wrong Setpoint Entered",
  "Manual Override Left Enabled",
  "Procedure Step Skipped",
  "Tool Left in Duct",
  "LLM Training Bias",
  "Sensor Name Misinterpretation",
  "Dust Storm Deposition",
  "Rapid Ambient Temperature Drop",
  "Trace Gas Sensor Chemistry Shift",
  "Radiation Soft Errors",
  "Orientation/Oil Return Issue",
  "External Shading Change",
  "Regolith Infiltration",
  "Ambient Pressure Variation",
  "Vibration Event Loose Connection",
  "Accidental Conduction Bridge",
  "Dual Fault: Leak + Sensor Bias",
  "Intermittent Inverter Throttle",
  "Latent TIM Pump-Out",
  "Return Leak + Thermostat Placement",
  "Time Skew + Threshold Mis-tuned",
  "Derate-Induced Short Cycling",
  "Dust + View-Factor Change"
]

print(len(possible_faults_136))

possible_faults = {
    "19": possible_faults_19,
    "22": possible_faults_22,
    "136": possible_faults_136,
}

def load_prompt(filepath: str) -> str:
    """Load prompt from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()