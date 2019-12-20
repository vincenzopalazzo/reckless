import os
from pyln.testing.fixtures import *  # noqa: F401,F403

plugin_path = os.path.join(os.path.dirname(__file__), "reckless.py")


def test_helpme_starts(node_factory):
    l1 = node_factory.get_node()
    # Test dynamically
    l1.rpc.plugin_start(plugin_path)
    l1.rpc.plugin_stop(plugin_path)
    l1.rpc.plugin_start(plugin_path)
    l1.stop()
    # Then statically
    l1.daemon.opts["plugin"] = plugin_path
    l1.start()


def test_install_basic(node_factory):
    l1 = node_factory.get_node()
    l1.rpc.plugin_start(plugin_path)
    urls = l1.rpc.call("search_plugin", {"keyword": "drain"})[0]
    # We got 2 results here, since there is Rene's one too !
    l1.rpc.call("install_plugin", {"url": urls["url_download"]})
    print(l1.rpc.plugin_list())
    l1.rpc.check("drain")


def test_install_from_keyword(node_factory):
    l1 = node_factory.get_node(options={"plugin": plugin_path})
    l1.rpc.call("install_plugin", {"url": "summary", "install_auto": True})
    l1.rpc.call("summary", {})


def test_install_submodule(node_factory):
    l1 = node_factory.get_node(options={"plugin": plugin_path})
    urls = l1.rpc.call("search_plugin", {"keyword": "lightning-qt"})[0]
    l1.rpc.call("install_plugin", {"url": urls["url_download"]})
    l1.rpc.check("gui")
