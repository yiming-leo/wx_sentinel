"""
规则加载与热重载模块
"""
import json
import threading
from tools.logger import get_logger

logger = get_logger("wx_sentinel")


class RuleLoader:
    """
    规则加载器
    负责加载 rules.json，支持热重载
    """

    def __init__(self, rules_path: str):
        """
        Args:
            rules_path: 规则文件的完整路径
        """
        self.rules_path = rules_path
        self.config = self._load()

    def _load(self) -> dict:
        """从文件加载规则配置"""
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info(f"规则加载成功: {self.rules_path} (规则数: {len(config.get('rules', []))})")
            return config
        except FileNotFoundError:
            logger.warning(f"规则文件不存在: {self.rules_path}，使用空配置")
            return {"rules": [], "default_reply": "", "bot_name": ""}
        except json.JSONDecodeError as e:
            logger.error(f"规则文件格式错误: {e}")
            return {"rules": [], "default_reply": "", "bot_name": ""}

    def reload(self):
        """热重载规则"""
        self.config = self._load()
        logger.info("规则已重新加载！")
        return self.config

    def start_watch(self):
        """
        启动热重载监听线程
        控制台输入 'r' 回车即可重新加载规则
        """
        print("💡 修改 rules.json 后，在控制台输入 'r' 回车即可热重载")

        def _watch():
            while True:
                try:
                    cmd = input().strip().lower()
                    if cmd == 'r':
                        self.reload()
                        print("✅ 规则已重新加载！")
                except EOFError:
                    break
                except Exception as e:
                    logger.error(f"热重载异常: {e}")

        thread = threading.Thread(target=_watch, daemon=True)
        thread.start()
        return thread