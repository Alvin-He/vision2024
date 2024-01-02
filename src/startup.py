import threading
import queue

import const as k
import helpers



def entry():



    tti_t = threading.Thread(helpers.tti().listen)
    tti_t.start()

