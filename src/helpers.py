import sys
import const as k
import _thread
import cv2

class namespace_global:

    @staticmethod
    def thr_q():
        _thread.interrupt_main()
        exit()

    @staticmethod
    def non_negative_or_0(num: float):
        if num < 0: num = 0
        return num
    
    @staticmethod
    def setCapRes640x480(cap):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

h = namespace_global


stdin = sys.stdin
class tti:
    def __init__(self):
        self.readBuffer: list[str] = []
        self.commands: dict[str, list[str]] = { 
            "help": [self.print_help, "Show this help message"],
            "clear": [self.clear_tty, "Clear the terminal"],
            "q": [lambda _=None: h.thr_q(), "quit the program"],
            "exit": [lambda _=None: h.thr_q(), "quit the program"]
        }
    
    def listen(self):
        self.print_help()
        while True:
            self.process_user_input()

    def _read(self):
        if not stdin.readable(): return
        self.readBuffer.append(stdin.readline())

    #consumes all following commands after one errors if there are more left in read buffer
    def cmd_error(self, reason="Unknown"):
        errarr = ["COMMAND ERROR! -- REASON: " + reason + " -- In:"]
        errarr.extend(self.readBuffer)
        print(*errarr, sep="\n\t", flush=True)
        self.readBuffer.clear()


    def process_user_input(self):
        self._read()
        if len(self.readBuffer) < 1: return

        cur_cmd_finished = False
        for i in range(len(self.readBuffer)):
            l = self.readBuffer[i]
            components = l.split()
            if len(components) < 1: 
                return self.cmd_error("Incorrect Syntax")
            
            name = components[0]
            carr = self.commands.get(name, [])
            if len(carr) == 0: return self.cmd_error("Command not found")
            num_args_expected = len(carr) - 2

            if (len(components) - 1) != num_args_expected: return self.cmd_error("Not enough arguments") 

            ret = carr[-2](*components[1:])

            if ret == False or ret == 0:
                return self.cmd_error("Command Failed during execution")
            print("finished")
            del self.readBuffer[0]

    def add_command(self, name: str, description: str, args: list, func_to_call):
        self.commands[name] = [*args, func_to_call, description]
    def add_alias(self, alias_name, origional_name):
        self.commands[alias_name] = self.commands[origional_name]

    def clear_tty(self):
        for _ in range(100):
            print("\n")

    def print_help(self):
        print(k.DESCRIPTION + " " + k.VERSION)
        print("Avliable commands:")
        for name in self.commands.keys():
            c_arr = self.commands[name]
            args = c_arr[:len(c_arr)-2]
            print(name, end="\t")
            for arg in args:
                print("<" + arg + ">",end=" ")
            print("  " + c_arr[-1], flush=True)



# cli = tti()

# command_capture = False

# # UI
# tti = tti()
# def tti_capture():
#     global command_capture
#     command_capture = True
# tti.add_command("capture", "capture an image to process for calib", [], tti_capture)


# tti.listen()