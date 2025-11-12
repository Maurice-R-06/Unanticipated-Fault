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

possible_faults = {
    "19": possible_faults_19,
    "22": possible_faults_22,
}

def load_prompt(filepath: str) -> str:
    """Load prompt from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()