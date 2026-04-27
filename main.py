import os
from wx4py import WeChatClient
from handler import RuleEngine, KeywordReplyHandler
from tools import switch_to_english_keyboard, setup_logger, RuleLoader

# ============ 日志初始化 ============
logger = setup_logger("wx_sentinel")

# ============ 键盘切换 ============
switch_to_english_keyboard()
logger.info("输入法已切换为英文键盘")

# ============ 规则加载 ============
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules", "test_rules.json")
ruler = RuleLoader(RULES_PATH)
rule_config = ruler.config
ruler.start_watch()

# ============ 监听群聊列表 ============
GROUPS = [
    "模拟DS E-LOG试运行问题反馈群",
    "模拟A * FOL RMS service",
    "模拟TEST RMS&E-LOG 试用问题反馈群"
]

# ============ 主入口 ============
if __name__ == "__main__":
    engine = RuleEngine(rule_config)

    with WeChatClient(auto_connect=True) as wx:
        handler = KeywordReplyHandler(wx, engine)
        logger.info(f"开始监听群聊... (规则数: {len(rule_config['rules'])})")
        wx.process_groups(GROUPS, [handler], block=True)