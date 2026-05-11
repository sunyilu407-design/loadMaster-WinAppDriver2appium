import logging, time, os, sys


BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# 定义日志文件路径
LOG_PATH = os.path.join(BASE_PATH, "log")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)


class Logger():
    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 确保只初始化一次
        if not Logger._initialized:
            self.logname = os.path.join(LOG_PATH, "{}.log".format(time.strftime("%Y%m%d")))
            self.logger = logging.getLogger("log")
            self.logger.setLevel(logging.DEBUG)

            # 清空已有的处理器，避免重复添加
            self.logger.handlers.clear()

            # 设置日志格式
            self.formater = logging.Formatter(
                '[%(asctime)s][%(filename)s %(lineno)d][%(levelname)s]: %(message)s')

            # 设置文件处理器，使用UTF-8编码
            self.filelogger = logging.FileHandler(self.logname, mode='a', encoding="UTF-8")
            
            # 设置控制台处理器
            self.console = logging.StreamHandler()
            self.console.setLevel(logging.DEBUG)
            
            # 设置日志级别
            self.filelogger.setLevel(logging.DEBUG)
            
            # 设置格式化器
            self.filelogger.setFormatter(self.formater)
            self.console.setFormatter(self.formater)
            
            # 添加处理器到logger
            self.logger.addHandler(self.filelogger)
            self.logger.addHandler(self.console)
            
            # 标记已初始化
            Logger._initialized = True
        
        # 确保输出不会因为编码问题而出现乱码
        if sys.stdout.encoding != 'utf-8':
            try:
                # 重新配置stdout以使用UTF-8编码
                sys.stdout.reconfigure(encoding='utf-8')
            except AttributeError:
                # Python < 3.7没有reconfigure方法
                pass




log = Logger().logger

if __name__ == '__main__':
    logger = Logger().logger
    logger.info("---测试开始---")
    logger.debug("---测试结束---")
