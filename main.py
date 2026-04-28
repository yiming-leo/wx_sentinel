import os
import atexit
from wx4py import WeChatClient
from handler import RuleEngine, KeywordReplyHandler
from tools import switch_to_english_keyboard, setup_logger, RuleLoader

# ============ 日志初始化 ============
logger = setup_logger("wx_sentinel")

# ============ 键盘切换 ============
switch_to_english_keyboard()
logger.info("输入法已切换为英文键盘")

# ============ 规则加载 ============
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules", "prod_rules.json")
ruler = RuleLoader(RULES_PATH)
rule_config = ruler.config

# 从这里取 groups，加个默认值防护
groups = rule_config.get("groups", [])
logger.info(f"配置加载完成: 群数={len(groups)}, 规则数={len(rule_config.get('rules', []))}, groups={groups}")

ruler.start_watch()


# ============ 程序退出时清理 ============
def cleanup():
    logger.info("程序退出")


atexit.register(cleanup)

# ============ 主入口 ============
if __name__ == "__main__":
    engine = RuleEngine(rule_config)

    with WeChatClient(auto_connect=True) as wx:
        handler = KeywordReplyHandler(wx, engine)
        logger.info(f"开始监听群聊...")
        wx.process_groups(groups, [handler], block=True)
