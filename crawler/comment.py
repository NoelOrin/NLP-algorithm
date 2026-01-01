import subprocess
import threading
import os
import sys

from crawler.weibo_comment_crawler.comment_crawler import run_comment_crawler

if __name__ == '__main__':
    # cookie = input("cookie: ")
    cookie= 'SCF=ArMQAAJmyIG49ARh17nK3PgjUV15xWAqieE_jmgpqmK6SjDbtkttYBrQnW5kx98k1R8HC7q0dJ9FfZb3KVH_1ys.; SINAGLOBAL=4456018209732.372.1766759621315; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh8HILbCB1TnVb5veiMiHfR5JpX5KzhUgL.Fo.7eo-Reh54e0e2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM4ehzf1h571Ke0; SUB=_2A25ESwjCDeRhGe9O6VcZ8C7FyD-IHXVnKQQKrDV8PUNbmtANLUHgkW9NdKWo_WYz_OvhpyYUPCTsqNWlPeiSm1hg; ALF=02_1769407890; UOR=,,cn.bing.com; ULV=1767107186673:2:2:1:1152742733714.024.1767107186670:1766759621322; XSRF-TOKEN=rrH4Hxxt5ssjVMIMF6ugf2GC; WBPSESS=orGjw7CWUWycH4biLvLUx5yoKsyZuEW6flxefWonNHb1F_ZVsMoV0gW4WFS6oV6GvWIAgn7MFNjnjsum-LHhhIDDaNytiG_CG5ylazEKkGFK6MoPN9gKjNN9gli6fcULiFT-J1AzzlfUl0AOUrthzw=='
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    run_comment_crawler(cookie)
