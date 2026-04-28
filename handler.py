"""
微信消息处理器模块
包含：规则匹配引擎 + 消息回复Handler
"""
import random
import time
import threading
from tools.logger import get_logger

logger = get_logger("wx_sentinel")


class RuleEngine:
    def __init__(self, config: dict):
        self.config = config

    def match(self, content: str) -> str:
        for rule in self.config.get("rules", []):
            keywords = rule.get("keywords", [])
            mode = rule.get("match_mode", "any")

            if mode == "all":
                if all(kw in content for kw in keywords):
                    return rule["reply"]
            else:
                if any(kw in content for kw in keywords):
                    return rule["reply"]

        # 默认回复：支持字符串或列表
        default = self.config.get("default_reply", "")
        if isinstance(default, list) and default:
            # ✅ 随机抽取一个元素
            return random.choice(default)
        return default


class KeywordReplyHandler:
    def __init__(self, wx_client, rule_engine: RuleEngine):
        self.wx = wx_client
        self.engine = rule_engine
        self._last_reply_time = {}      # 记录每个群最后一次回复时间
        self._cooldown = 60             # 冷却秒数（可从配置读取）

    def set_action_emitter(self, emitter):
        self.emitter = emitter

    def stop(self):
        pass

    def _is_at_me(self, content: str) -> bool:
        bot_name = self.engine.config.get("bot_name", "")
        if not bot_name:
            return True
        return bot_name in content

    def _is_in_cooldown(self, group: str) -> bool:
        """检查该群是否在冷却中"""
        last_time = self._last_reply_time.get(group, 0)
        elapsed = time.time() - last_time
        if elapsed < self._cooldown:
            logger.debug(f"[{group}] 冷却中 ({elapsed:.0f}s/{self._cooldown}s)，跳过")
            return True
        return False

    def _update_cooldown(self, group: str):
        """更新最后一次回复时间"""
        self._last_reply_time[group] = time.time()

    def handle(self, event):
        group = event.group
        content = event.content

        logger.info(f"[{group}] {content}")

        # 检查冷却
        if self._is_in_cooldown(group):
            return

        if self.engine.config.get("reply_only_on_at", True):
            if not self._is_at_me(content):
                logger.debug("不是@我的消息，跳过")
                return

        reply_text = self.engine.match(content)

        if not reply_text:
            logger.debug(f"无匹配规则，跳过: {content}")
            return

        # 标记冷却（发送前就先锁上，防止并发）
        self._update_cooldown(group)

        delay = self.engine.config.get("delay_seconds", 0)
        logger.info(f"匹配成功，{delay}秒后回复: {reply_text}")

        def delayed_reply(text):
            if delay > 0:
                time.sleep(delay)
            try:
                self.wx.chat_window.send_to(group, text, target_type='group')
                logger.info(f"已发送到 {group}: {text}")
            except Exception as e:
                logger.error(f"发送失败: {e}")
                # 发送失败时取消冷却，允许重试
                self._last_reply_time.pop(group, None)

        threading.Thread(target=delayed_reply, args=(reply_text,), daemon=True).start()