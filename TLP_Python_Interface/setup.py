from cx_Freeze import setup, Executable
  
setup(name = "TLPPI" ,
      version = "1.0" ,
      description = "ThorLabs Piezocontroller Python Interface" ,
      executables = [Executable("TLPPI.py")])