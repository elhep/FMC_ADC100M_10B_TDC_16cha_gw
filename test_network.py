import subprocess as sp
import signal
import sys
import time

run = True
result = []
i = 0

def signal_handler(sig, frame):
    run = False
    print("")

signal.signal(signal.SIGINT, signal_handler)

def preexec_function():
    run = False
    signal.signal(signal.SIGINT, signal.SIG_IGN)


N = 500
FPGA_BOOT_CMD = "artiq_flash -I \"ftdi_location 1:3,1,1\" -d ./ --srcbuild -V build -t afck1v1 load"
SW_BOOT_CMD = "artiq_netboot -f ./build/software/runtime/runtime.bin -b 192.168.1.203"


def boot_afck(boot_fpga=True, boot_sw=True):
    if boot_fpga:
        child = sp.Popen(["dartiq", "run", FPGA_BOOT_CMD], stdout=sp.PIPE, preexec_fn=preexec_function)
        streamdata = child.communicate()[0]
        fpga_boot_rc = child.returncode

        if fpga_boot_rc != 0:
            return f"FPGA BOOT FAILED ({fpga_boot_rc})"

    if boot_sw:
        time.sleep(5.0)
        child = sp.Popen(["dartiq", "run", SW_BOOT_CMD], stdout=sp.PIPE)
        streamdata = child.communicate()[0]
        sw_boot_rc = child.returncode

        if sw_boot_rc != 0:
            return f"SW BOOT FAILED ({sw_boot_rc})"
    
    return "OK"
    

with open("network_results.csv", 'w'): pass

for n in range(N):
    if not run:
        break
    
    t0 = time.time()
    print(f"{n}: ", end='', flush=True)
    result = boot_afck()
    duration = time.time()-t0
    print(result, f"took: {duration} sec.")

    with open("network_results.csv", "a") as f:
        f.write(f"{n}, {result}, {duration}\n")
