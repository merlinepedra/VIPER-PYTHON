# -*- coding: utf-8 -*-
# @File  : xcache.py
# @Date  : 2021/2/25
# @Desc  :
import copy
import time
import uuid

from django.core.cache import cache

from CONFIG import DEBUG
from Lib.configs import EXPIRE_MINUTES
from Lib.log import logger


class Xcache(object):
    """缓存模块"""
    XCACHE_MODULES_CONFIG = "XCACHE_MODULES_CONFIG"

    XCACHE_SESSION_INFO = "XCACHE_SESSION_INFO"

    XCACHE_HOST_INFO = "XCACHE_HOST_INFO"

    XCACHE_HADLER_VIRTUAL_LIST = "XCACHE_HADLER_VIRTUAL_LIST"

    XCACHE_HADLER_CACHE = "XCACHE_HADLER_CACHE"

    XCACHE_NOTICES_LIST = "XCACHE_NOTICES_LIST"

    XCACHE_MODULES_TASK_LIST = "XCACHE_MODULES_TASK_LIST"

    XCACHE_BOT_MODULES_WAIT_LIST = "XCACHE_BOT_MODULES_WAIT_LIST"

    XCACHE_MODULES_RESULT = "XCACHE_MODULES_RESULT"
    XCACHE_MODULES_RESULT_HISTORY = "XCACHE_MODULES_RESULT_HISTORY"
    XCACHE_HEARTBEAT_CACHE_RESULT_HISTORY = "XCACHE_HEARTBEAT_CACHE_RESULT_HISTORY"
    XCACHE_HEARTBEAT_CACHE_NOTICES = "XCACHE_HEARTBEAT_CACHE_NOTICES"
    XCACHE_HEARTBEAT_CACHE_JOBS = "XCACHE_HEARTBEAT_CACHE_JOBS"
    XCACHE_HEARTBEAT_CACHE_BOT_WAIT_LIST = "XCACHE_HEARTBEAT_CACHE_BOT_WAIT_LIST"
    XCACHE_HEARTBEAT_CACHE_HOSTS_SORTED = "XCACHE_HEARTBEAT_CACHE_HOSTS_SORTED"
    XCACHE_HEARTBEAT_CACHE_NETWORK_DATA = "XCACHE_HEARTBEAT_CACHE_NETWORK_DATA"

    XCACHE_MSFCONSOLE_INPUT_CACHE = "XCACHE_MSFCONSOLE_INPUT_CACHE"
    XCACHE_MSFCONSOLE_CID = "XCACHE_MSFCONSOLE_CID"
    XCACHE_MSFCONSOLE_HISTORY_CACHE = "XCACHE_MSFCONSOLE_HISTORY_CACHE"
    XCACHE_MSFCONSOLE_HISTORY_CURSOR = "XCACHE_MSFCONSOLE_HISTORY_CURSOR"

    XCACHE_MSF_JOB_CACHE = "XCACHE_MSF_JOB_CACHE"

    XCACHE_TELEGRAM_CONFIG = "XCACHE_TELEGRAM_CONFIG"
    XCACHE_DINGDING_CONFIG = "XCACHE_DINGDING_CONFIG"
    XCACHE_SERVERCHAN_CONFIG = "XCACHE_SERVERCHAN_CONFIG"
    XCACHE_FOFA_CONFIG = "XCACHE_FOFA_CONFIG"
    XCACHE_QUAKE_CONFIG = "XCACHE_QUAKE_CONFIG"
    XCACHE_SESSIONMONITOR_CONFIG = "XCACHE_SESSIONMONITOR_CONFIG"

    XCACHE_SESSION_LIST = "XCACHE_SESSION_LIST"

    XCACHE_AES_KEY = "XCACHE_AES_KEY"

    XCACHE_NETWORK_TOPOLOGY = "XCACHE_NETWORK_TOPOLOGY"

    XCACHE_GEOIP_CITYREADER = "XCACHE_GEOIP_CITYREADER"
    XCACHE_GEOIP_ASNREADER = "XCACHE_GEOIP_ASNREADER"

    XCACHE_MSFRPC_CONFIG = "XCACHE_MSFRPC_CONFIG"

    XCACHE_SESSIONIO_CACHE = "XCACHE_SESSIONIO_CACHE"

    XCACHE_LAZYLOADER_CACHE = "XCACHE_LAZYLOADER_CACHE"

    XCACHE_LOGIN_FAIL_COUNT = "XCACHE_LOGIN_FAIL_COUNT"

    XCACHE_POSTMODULE_AUTO_LIST = "XCACHE_POSTMODULE_AUTO_LIST"

    XCACHE_POSTMODULE_AUTO_CONF = "XCACHE_POSTMODULE_AUTO_CONF"

    XCACHE_TOKEN = "XCACHE_TOKEN"

    XCACHE_MSFRPC_ERROR_LOG = "XCACHE_MSFRPC_ERROR_LOG"

    def __init__(self):
        pass

    @staticmethod
    def get_postmodule_auto_dict():
        """获取自动化模块配置字典"""
        result = cache.get(Xcache.XCACHE_POSTMODULE_AUTO_LIST)
        if result is None:
            return {}
        return result

    @staticmethod
    def add_postmodule_auto_list(module_uuid, loadpath, custom_param):
        """新增一个自动化模块配置到有序字典"""
        result = cache.get(Xcache.XCACHE_POSTMODULE_AUTO_LIST)
        if result is None:
            result = {}
        result[module_uuid] = {"loadpath": loadpath, "custom_param": custom_param}
        cache.set(Xcache.XCACHE_POSTMODULE_AUTO_LIST, result, None)
        return True

    @staticmethod
    def set_postmodule_auto_conf(conf):
        old_conf = cache.get(Xcache.XCACHE_POSTMODULE_AUTO_CONF)

        if old_conf is None:
            old_conf = {"flag": False, "interval": 1, "max_session": 3}
        if old_conf.get("interval") is None:
            old_conf["interval"] = 1
        if old_conf.get("max_session") is None:
            old_conf["max_session"] = 3

        old_conf.update(conf)
        cache.set(Xcache.XCACHE_POSTMODULE_AUTO_CONF, old_conf, None)
        return old_conf

    @staticmethod
    def get_postmodule_auto_conf():
        conf = cache.get(Xcache.XCACHE_POSTMODULE_AUTO_CONF)
        if conf is None:
            return {"flag": False, "interval": 1, "max_session": 3}
        return conf

    @staticmethod
    def delete_postmodule_auto_list(module_uuid):
        """从字典中删除一个自动化模块配置"""
        result = cache.get(Xcache.XCACHE_POSTMODULE_AUTO_LIST)
        if result is None:
            result = {}
        result.pop(module_uuid)
        cache.set(Xcache.XCACHE_POSTMODULE_AUTO_LIST, result, None)
        return True

    @staticmethod
    def init_xcache_on_start():
        # 清理模块配置缓存
        cache.set(Xcache.XCACHE_MODULES_CONFIG, None, None)

        # 清理muit_module缓存
        re_key = "{}_*".format(Xcache.XCACHE_MODULES_TASK_LIST)
        keys = cache.keys(re_key)
        for key in keys:
            try:
                req = cache.get(key)
            except Exception as _:
                cache.delete(key)
                continue
            if req.get("job_id") is None:
                cache.delete(key)

        # 清理session_info缓存
        re_key = "{}_*".format(Xcache.XCACHE_SESSION_INFO)
        keys = cache.keys(re_key)
        for key in keys:
            try:
                cache.delete(key)
            except Exception as _:
                continue
        if DEBUG is not True:
            Xcache.clean_all_token()
        return True

    @staticmethod
    def get_heartbeat_cache_hosts_sorted():
        result = cache.get(Xcache.XCACHE_HEARTBEAT_CACHE_HOSTS_SORTED)
        return result

    @staticmethod
    def set_heartbeat_cache_hosts_sorted(result):
        cache.set(Xcache.XCACHE_HEARTBEAT_CACHE_HOSTS_SORTED, result, None)
        return True

    @staticmethod
    def get_heartbeat_cache_network_data():
        result = cache.get(Xcache.XCACHE_HEARTBEAT_CACHE_NETWORK_DATA)
        return result

    @staticmethod
    def set_heartbeat_cache_network_data(result):
        cache.set(Xcache.XCACHE_HEARTBEAT_CACHE_NETWORK_DATA, result, None)
        return True

    @staticmethod
    def get_heartbeat_cache_result_history():
        result = cache.get(Xcache.XCACHE_HEARTBEAT_CACHE_RESULT_HISTORY)
        return result

    @staticmethod
    def set_heartbeat_cache_result_history(result):
        cache.set(Xcache.XCACHE_HEARTBEAT_CACHE_RESULT_HISTORY, result, None)
        return True

    @staticmethod
    def get_heartbeat_cache_notices():
        result = cache.get(Xcache.XCACHE_HEARTBEAT_CACHE_NOTICES)
        return result

    @staticmethod
    def set_heartbeat_cache_notices(result):
        cache.set(Xcache.XCACHE_HEARTBEAT_CACHE_NOTICES, result, None)
        return True

    @staticmethod
    def get_heartbeat_cache_jobs():
        result = cache.get(Xcache.XCACHE_HEARTBEAT_CACHE_JOBS)
        return result

    @staticmethod
    def set_heartbeat_cache_jobs(result):
        cache.set(Xcache.XCACHE_HEARTBEAT_CACHE_JOBS, result, None)
        return True

    @staticmethod
    def get_heartbeat_cache_bot_wait_list():
        result = cache.get(Xcache.XCACHE_HEARTBEAT_CACHE_BOT_WAIT_LIST)
        return result

    @staticmethod
    def set_heartbeat_cache_bot_wait_list(result):
        cache.set(Xcache.XCACHE_HEARTBEAT_CACHE_BOT_WAIT_LIST, result, None)
        return True

    @staticmethod
    def get_msf_job_cache():
        result = cache.get(Xcache.XCACHE_MSF_JOB_CACHE)
        return result

    @staticmethod
    def set_msf_job_cache(msfjobs):
        cache.set(Xcache.XCACHE_MSF_JOB_CACHE, msfjobs, None)
        return True

    @staticmethod
    def get_module_task_by_uuid(task_uuid):
        for i in range(2):
            key = "{}_{}".format(Xcache.XCACHE_MODULES_TASK_LIST, task_uuid)
            req = cache.get(key)
            if req is not None:
                return req
            else:
                pass
            time.sleep(1)

    @staticmethod
    def get_module_task_by_uuid_nowait(task_uuid):
        key = "{}_{}".format(Xcache.XCACHE_MODULES_TASK_LIST, task_uuid)
        req = cache.get(key)
        return req

    @staticmethod
    def list_module_tasks():
        re_key = "{}_*".format(Xcache.XCACHE_MODULES_TASK_LIST)
        keys = cache.keys(re_key)
        reqs = []
        for key in keys:
            reqs.append(cache.get(key))
        return reqs

    @staticmethod
    def create_module_task(req):
        """任务队列"""
        for i in range(5):
            key = "{}_{}".format(Xcache.XCACHE_MODULES_TASK_LIST, req.get("uuid"))
            cache.set(key, req, None)
            if cache.get(key) is not None:
                break
            else:
                logger.error("redis 缓存失败!")
            time.sleep(0.5)
        return True

    @staticmethod
    def del_module_task_by_uuid(task_uuid):
        key = "{}_{}".format(Xcache.XCACHE_MODULES_TASK_LIST, task_uuid)
        cache.delete(key)

    # XCACHE_BOT_MODULES_WAIT_LIST

    @staticmethod
    def pop_one_from_bot_wait():
        re_key = "{}_*".format(Xcache.XCACHE_BOT_MODULES_WAIT_LIST)
        keys = cache.keys(re_key)

        for key in keys:
            req = cache.get(key)
            if req is not None:
                cache.delete(key)
                return req
        return None

    @staticmethod
    def list_bot_wait():
        re_key = "{}_*".format(Xcache.XCACHE_BOT_MODULES_WAIT_LIST)

        keys = cache.keys(re_key)
        reqs = []
        for key in keys:
            reqs.append(cache.get(key))
        return reqs

    @staticmethod
    def putin_bot_wait(req):
        """任务队列"""
        key = "{}_{}".format(Xcache.XCACHE_BOT_MODULES_WAIT_LIST, req.get("uuid"))
        cache.set(key, req, None)
        return True

    @staticmethod
    def del_bot_wait_by_group_uuid(group_uuid):
        re_key = "{}_*".format(Xcache.XCACHE_BOT_MODULES_WAIT_LIST)
        keys = cache.keys(re_key)
        for key in keys:
            req = cache.get(key)
            if req.get("group_uuid") == group_uuid:
                cache.delete(key)
        return True

    @staticmethod
    def get_module_result(ipaddress, loadpath):
        key = "{}_{}_{}".format(Xcache.XCACHE_MODULES_RESULT, ipaddress, loadpath)
        result_dict = cache.get(key)
        if result_dict is None:
            return {"update_time": int(time.time()), "result": ""}
        return result_dict

    @staticmethod
    def set_module_result(ipaddress, loadpath, result):
        key = "{}_{}_{}".format(Xcache.XCACHE_MODULES_RESULT, ipaddress, loadpath)

        cache.set(key, {"update_time": int(time.time()), "result": result}, None)
        return True

    @staticmethod
    def add_module_result(ipaddress, loadpath, result):
        key = "{}_{}_{}".format(Xcache.XCACHE_MODULES_RESULT, ipaddress, loadpath)
        old_result = cache.get(key)
        if old_result is None:
            new_result = result
        else:
            new_result = old_result.get("result") + result

        cache.set(key, {"update_time": int(time.time()), "result": new_result}, None)
        return True

    @staticmethod
    def del_module_result_by_ipaddress(ipaddress):
        re_key = "{}_{}_*".format(Xcache.XCACHE_MODULES_RESULT, ipaddress)
        keys = cache.keys(re_key)
        for key in keys:
            cache.set(key, None, None)
        return True

    @staticmethod
    def list_module_result_history():
        result = cache.get(Xcache.XCACHE_MODULES_RESULT_HISTORY)
        if result is None:
            return []
        return result[::-1]

    @staticmethod
    def add_module_result_history(ipaddress=None, loadpath=None, opts=None, update_time=0, result=""):
        if opts is None:
            opts = []
        one_result = {"ipaddress": ipaddress,
                      "loadpath": loadpath,
                      "opts": opts,
                      "update_time": update_time,
                      "result": result}
        old_result = cache.get(Xcache.XCACHE_MODULES_RESULT_HISTORY)
        if old_result is None:
            cache.set(Xcache.XCACHE_MODULES_RESULT_HISTORY, [one_result], None)
        else:
            old_result.append(one_result)
            cache.set(Xcache.XCACHE_MODULES_RESULT_HISTORY, old_result, None)

        return True

    @staticmethod
    def del_module_result_history():
        cache.set(Xcache.XCACHE_MODULES_RESULT_HISTORY, [], None)
        return True

    @staticmethod
    def del_module_result_history_by_ipaddress(ipaddress):
        old_result = cache.get(Xcache.XCACHE_MODULES_RESULT_HISTORY)
        if old_result is None:
            return False
        else:
            new_result = []
            for one_result in old_result:
                if one_result.get("ipaddress") != ipaddress:
                    new_result.append(one_result)

            cache.set(Xcache.XCACHE_MODULES_RESULT_HISTORY, new_result, None)
        return True

    @staticmethod
    def get_module_task_length():
        re_key = "{}_*".format(Xcache.XCACHE_MODULES_TASK_LIST)
        keys = cache.keys(re_key)
        return len(keys)

    @staticmethod
    def get_notices():
        notices = cache.get(Xcache.XCACHE_NOTICES_LIST)
        if notices is None:
            return []
        else:
            notices.reverse()
            return notices[0:200]

    @staticmethod
    def clean_notices():
        cache.set(Xcache.XCACHE_NOTICES_LIST, [], None)
        return True

    @staticmethod
    def add_one_notice(notice):
        notices = cache.get(Xcache.XCACHE_NOTICES_LIST)
        if notices is None:
            cache.set(Xcache.XCACHE_NOTICES_LIST, [notice], None)
        else:
            tempnotices = copy.deepcopy(notices)
            tempnotices.append(notice)
            cache.set(Xcache.XCACHE_NOTICES_LIST, tempnotices, None)

    @staticmethod
    def list_moduleconfigs():
        modules_config = cache.get(Xcache.XCACHE_MODULES_CONFIG)
        if modules_config is None:
            return None
        else:
            return modules_config

    @staticmethod
    def update_moduleconfigs(all_modules_config):
        cache.set(Xcache.XCACHE_MODULES_CONFIG, all_modules_config, None)
        return True

    @staticmethod
    def get_moduleconfig(loadpath):
        modules_config = cache.get(Xcache.XCACHE_MODULES_CONFIG)
        try:
            for config in modules_config:
                if config.get("loadpath") == loadpath:
                    return config
            return None
        except Exception as E:
            logger.error(E)
            return None

    @staticmethod
    def set_session_info(sessionid, session_info):
        key = "{}_{}".format(Xcache.XCACHE_SESSION_INFO, sessionid)
        cache.set(key, session_info, None)
        return True

    @staticmethod
    def get_session_info(sessionid):
        key = "{}_{}".format(Xcache.XCACHE_SESSION_INFO, sessionid)
        session_info = cache.get(key)
        return session_info

    @staticmethod
    def get_host_info(ipaddress):
        key = "{}_{}".format(Xcache.XCACHE_HOST_INFO, ipaddress)
        host_info = cache.get(key)
        if host_info is None:
            return {}
        return host_info

    @staticmethod
    def update_host_info(ipaddress, new_value: dict):
        key = "{}_{}".format(Xcache.XCACHE_HOST_INFO, ipaddress)
        host_info_old = Xcache.get_host_info(ipaddress)
        host_info_old.update(new_value)
        cache.set(key, host_info_old, None)
        return host_info_old

    @staticmethod
    def del_host_info(ipaddress):
        key = "{}_{}".format(Xcache.XCACHE_HOST_INFO, ipaddress)
        try:
            cache.delete(key)
            return True
        except Exception as _:
            return False

    @staticmethod
    def get_virtual_handlers():
        handler_list = cache.get(Xcache.XCACHE_HADLER_VIRTUAL_LIST)
        if handler_list is None:
            handler_list = []
        return handler_list

    @staticmethod
    def set_cache_handlers(handler_list):
        cache.set(Xcache.XCACHE_HADLER_CACHE, handler_list, None)
        return True

    @staticmethod
    def get_cache_handlers():
        handler_list = cache.get(Xcache.XCACHE_HADLER_CACHE)
        if handler_list is None:
            handler_list = []
        return handler_list

    @staticmethod
    def add_virtual_handler(onehandler):
        handler_list = cache.get(Xcache.XCACHE_HADLER_VIRTUAL_LIST)
        if handler_list is None:
            handler_list = []

        minid = -1

        for handler in handler_list:
            tmphandler = copy.copy(handler)
            tmpid = tmphandler.pop('ID')
            tmphandler.pop('timestamp')

            tmphandler1 = copy.copy(onehandler)
            tmphandler1.pop('timestamp')
            if tmphandler == tmphandler1:
                return tmpid
            if tmpid <= minid:
                minid = tmpid

        handler_id = minid - 1
        onehandler['ID'] = handler_id
        handler_list.append(onehandler)
        cache.set(Xcache.XCACHE_HADLER_VIRTUAL_LIST, handler_list, None)
        return handler_id

    @staticmethod
    def del_virtual_handler(virtual_id):
        handler_list = cache.get(Xcache.XCACHE_HADLER_VIRTUAL_LIST)
        if handler_list is None:
            handler_list = []
            cache.set(Xcache.XCACHE_HADLER_VIRTUAL_LIST, handler_list, None)
            return False
        for onehandler in handler_list:
            if onehandler.get('ID') == virtual_id:
                handler_list.remove(onehandler)
        cache.set(Xcache.XCACHE_HADLER_VIRTUAL_LIST, handler_list, None)
        return True

    @staticmethod
    def add_to_msfconsoleinputcache(data):
        inputcache = cache.get(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE)
        if inputcache is None:
            cache.set(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE, data, None)
            return data
        else:
            cache.set(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE, inputcache + data, None)
            return inputcache + data

    @staticmethod
    def del_one_from_msfconsoleinputcache():
        inputcache = cache.get(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE)
        if inputcache is None or inputcache == "":
            return "\u0007"
        else:
            cache.set(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE, inputcache[0:-1], None)
            return "\b\u001b[K"

    @staticmethod
    def clear_oneline_from_msfconsoleinputcache():
        inputcache = cache.get(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE)
        if inputcache is None or inputcache == "":
            return "\u0007"
        else:
            cache.set(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE, "", None)
            return "\b\u001b[K" * len(inputcache)

    @staticmethod
    def get_msfconsoleinputcache():
        inputcache = cache.get(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE)
        if inputcache is None:
            return ""
        else:
            return inputcache

    @staticmethod
    def clean_msfconsoleinputcache():
        cache.set(Xcache.XCACHE_MSFCONSOLE_INPUT_CACHE, "", None)
        return True

    @staticmethod
    def add_to_msfconsole_history_cache(cmd):
        if cmd is None or cmd == "":
            return True
        historys = cache.get(Xcache.XCACHE_MSFCONSOLE_HISTORY_CACHE)
        cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR, 0, None)  # 重置光标
        if historys is None:
            cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CACHE, [cmd], None)
            return True
        else:
            historys.insert(0, cmd)
            cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CACHE, historys, None)
            return True

    @staticmethod
    def get_last_from_msfconsole_history_cache():
        historys = cache.get(Xcache.XCACHE_MSFCONSOLE_HISTORY_CACHE)
        if historys is None or len(historys) == 0:
            return None
        cursor = cache.get(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR)
        if cursor is None:
            cursor = 0
            cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR, 1, None)  # 重置光标
        else:
            cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR, cursor + 1, None)  # 重置光标
        cursor %= len(historys)
        return historys[cursor]

    @staticmethod
    def get_next_from_msfconsole_history_cache():
        historys = cache.get(Xcache.XCACHE_MSFCONSOLE_HISTORY_CACHE)
        if historys is None or len(historys) == 0:
            return None
        cursor = cache.get(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR)
        if cursor is None or cursor == 0:
            cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR, 0, None)
            return None
        else:
            cache.set(Xcache.XCACHE_MSFCONSOLE_HISTORY_CURSOR, cursor - 1, None)  # 重置光标
        cursor %= len(historys)
        return historys[cursor]

    @staticmethod
    def set_console_id(cid):
        cache.set(Xcache.XCACHE_MSFCONSOLE_CID, cid, None)
        return True

    @staticmethod
    def get_console_id():
        inputcache = cache.get(Xcache.XCACHE_MSFCONSOLE_CID)
        return inputcache

    @staticmethod
    def alive_token(token):
        key = f"{Xcache.XCACHE_TOKEN}-{token}"
        cache_user = cache.get(key)
        return cache_user

    @staticmethod
    def set_token_user(token, user):
        key = f"{Xcache.XCACHE_TOKEN}-{token}"
        cache.set(key, user, EXPIRE_MINUTES)

    @staticmethod
    def clean_all_token():
        re_key = "{}-*".format(Xcache.XCACHE_TOKEN)
        keys = cache.keys(re_key)
        for key in keys:
            req = cache.delete(key)

    @staticmethod
    def set_telegram_conf(conf):
        cache.set(Xcache.XCACHE_TELEGRAM_CONFIG, conf, None)
        return True

    @staticmethod
    def get_telegram_conf():
        conf = cache.get(Xcache.XCACHE_TELEGRAM_CONFIG)
        return conf

    @staticmethod
    def set_dingding_conf(conf):
        cache.set(Xcache.XCACHE_DINGDING_CONFIG, conf, None)
        return True

    @staticmethod
    def get_dingding_conf():
        conf = cache.get(Xcache.XCACHE_DINGDING_CONFIG)
        return conf

    @staticmethod
    def set_serverchan_conf(conf):
        cache.set(Xcache.XCACHE_SERVERCHAN_CONFIG, conf, None)
        return True

    @staticmethod
    def get_serverchan_conf():
        conf = cache.get(Xcache.XCACHE_SERVERCHAN_CONFIG)
        return conf

    @staticmethod
    def set_fofa_conf(conf):
        cache.set(Xcache.XCACHE_FOFA_CONFIG, conf, None)
        return True

    @staticmethod
    def get_fofa_conf():
        conf = cache.get(Xcache.XCACHE_FOFA_CONFIG)
        if conf is None:
            return {"email": None, "key": None, "alive": False}
        return conf

    @staticmethod
    def set_quake_conf(conf):
        cache.set(Xcache.XCACHE_QUAKE_CONFIG, conf, None)
        return True

    @staticmethod
    def get_quake_conf():
        conf = cache.get(Xcache.XCACHE_QUAKE_CONFIG)
        if conf is None:
            return {"key": None, "alive": True}
        return conf

    @staticmethod
    def set_sessionmonitor_conf(conf):
        cache.set(Xcache.XCACHE_SESSIONMONITOR_CONFIG, conf, None)
        return True

    @staticmethod
    def get_sessionmonitor_conf():
        conf = cache.get(Xcache.XCACHE_SESSIONMONITOR_CONFIG)
        if conf is None:
            conf = {"flag": False}
            cache.set(Xcache.XCACHE_SESSIONMONITOR_CONFIG, conf, None)
        return conf

    @staticmethod
    def set_session_count(count):
        cache.set(Xcache.XCACHE_SESSION_LIST, count, None)
        return True

    @staticmethod
    def get_session_count():
        conf = cache.get(Xcache.XCACHE_SESSION_LIST)
        if conf is None:
            return 0
        return conf

    @staticmethod
    def update_session_list(sessions):
        old_sessions_dict = cache.get(Xcache.XCACHE_SESSION_LIST)
        if old_sessions_dict is None:
            old_sessions_dict = {}
        return_sessions_dict = {}
        new_sessions_dict = {}
        for session in sessions:
            if session.get("available"):
                session_uuid = session.get("uuid")
                new_sessions_dict[session_uuid] = session
                if old_sessions_dict.get(session.get("uuid")) is None:
                    return_sessions_dict[session_uuid] = session

        cache.set(Xcache.XCACHE_SESSION_LIST, new_sessions_dict, None)
        return return_sessions_dict

    @staticmethod
    def get_lhost_config():
        cache_data = cache.get(Xcache.XCACHE_MSFRPC_CONFIG)
        return cache_data

    @staticmethod
    def set_lhost_config(cache_data):
        cache.set(Xcache.XCACHE_MSFRPC_CONFIG, cache_data, None)
        return True

    @staticmethod
    def get_aes_key():
        conf = cache.get(Xcache.XCACHE_AES_KEY)
        if conf is None:
            tmp_self_uuid = str(uuid.uuid1()).replace('-', "")[0:16]
            cache.set(Xcache.XCACHE_AES_KEY, tmp_self_uuid, None)
            return tmp_self_uuid
        else:
            return conf

    @staticmethod
    def set_network_topology_cache(cache_data):
        cache.set(Xcache.XCACHE_NETWORK_TOPOLOGY, cache_data)
        return True

    @staticmethod
    def get_network_topology_cache():
        cache_data = cache.get(Xcache.XCACHE_NETWORK_TOPOLOGY)
        return cache_data

    @staticmethod
    def get_sessionio_cache(ipaddress):
        cache_dict = cache.get(Xcache.XCACHE_SESSIONIO_CACHE)
        if cache_dict is None:
            cache_dict = {ipaddress: ''}
            cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
            return {'ipaddress': ipaddress, 'buffer': ''}

        if cache_dict.get(ipaddress) is None:
            cache_dict[ipaddress] = ''
            cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
            return {'ipaddress': ipaddress, 'buffer': ''}
        old_buffer = cache_dict.get(ipaddress)
        return {'ipaddress': ipaddress, 'buffer': old_buffer}

    @staticmethod
    def add_sessionio_cache(ipaddress, buffer):
        cache_dict = cache.get(Xcache.XCACHE_SESSIONIO_CACHE)
        if cache_dict is None:
            cache_dict = {ipaddress: buffer}
            cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
            return {'ipaddress': ipaddress, 'buffer': buffer}
        if cache_dict.get(ipaddress) is None:
            cache_dict[ipaddress] = buffer
            cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
            return {'ipaddress': ipaddress, 'buffer': buffer}

        new_buffer = cache_dict.get(ipaddress) + buffer
        cache_dict[ipaddress] = new_buffer
        cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
        return {'ipaddress': ipaddress, 'buffer': new_buffer}

    @staticmethod
    def del_sessionio_cache(ipaddress):
        cache_dict = cache.get(Xcache.XCACHE_SESSIONIO_CACHE)
        if cache_dict is None:
            cache_dict = {ipaddress: ''}
            cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
            return {'ipaddress': ipaddress, 'buffer': ''}
        cache_dict[ipaddress] = ''
        cache.set(Xcache.XCACHE_SESSIONIO_CACHE, cache_dict)
        return {'ipaddress': ipaddress, 'buffer': ''}

    @staticmethod
    def list_lazyloader():
        re_key = "{}_*".format(Xcache.XCACHE_LAZYLOADER_CACHE)
        keys = cache.keys(re_key)
        reqs = []
        for key in keys:
            req = cache.get(key)
            reqs.append(req)
        return reqs

    @staticmethod
    def get_lazyloader_by_uuid(loader_uuid):
        key = f"{Xcache.XCACHE_LAZYLOADER_CACHE}_{loader_uuid}"
        data = cache.get(key)
        return data

    @staticmethod
    def set_lazyloader_by_uuid(loader_uuid, data):
        key = f"{Xcache.XCACHE_LAZYLOADER_CACHE}_{loader_uuid}"
        cache.set(key, data, None)
        return True

    @staticmethod
    def del_lazyloader_by_uuid(loader_uuid):
        key = f"{Xcache.XCACHE_LAZYLOADER_CACHE}_{loader_uuid}"
        cache.delete(key)
        return True

    @staticmethod
    def login_fail_count():
        key = f"{Xcache.XCACHE_LOGIN_FAIL_COUNT}"
        count = cache.get(key)
        if count is None:  # 第一次错误
            cache.set(key, 1, 60 * 10)  # 10分钟计时周期
        elif count == -1:  # 已经发送报警
            return False
        elif count >= 10:  # 发送报警
            cache.set(key, -1, 60 * 10)  # 10分钟计时周期
            return True
        else:
            count += 1
            cache.set(key, count, 60 * 10)  # 10分钟计时周期
            return False

    @staticmethod
    def msfrpc_error_send():
        flag = cache.get(Xcache.XCACHE_MSFRPC_ERROR_LOG)
        if flag:
            return False
        else:
            cache.set(Xcache.XCACHE_MSFRPC_ERROR_LOG, True, 30)  # 10秒计时周期
            return True
