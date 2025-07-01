import _ from "lodash";
import Ws from "@/utils/web_socket/ws";
import {
  WS_MSG_NOENCRYPT,
  WS_MSG_TYPE_STARTSTATUS,
  SERVERURL,
} from "@/utils/web_socket/define";

/**
 * ArxApi调用封装
 */
class WsApi {
  badmitonServerUrl;
  arxConnection = { iframeUrl: undefined, arxServerUrl: undefined };
  arx_ws;

  constructor(badmitonServerUrl) {
    this.badmitonServerUrl = badmitonServerUrl;
  }

  /**
   * 启动arx,获取iframe地址,底板websocket服务地址
   * @param string templateId
   * @param number screenWidth
   * @param number screenHeight
   * @param Function callback 回调参数 {iframeUrl:"",arxServerUrl:""}
   * @param number ratio arx服务返回给屏幕的比率
   */
  getArxConnection(
    templateId,
    screenWidth,
    screenHeight,
    callback,
    ratio = 1,
    arxGroup = "IssMeta"
  ) {
    const badmiton_ws = new Ws(SERVERURL);
    badmiton_ws.send(WS_MSG_NOENCRYPT);
    const arxReqMsg = `webRequestStart|${templateId}|${screenWidth},${screenHeight}|${ratio}|${arxGroup}$`;
    badmiton_ws.send(arxReqMsg);
    console.log("request Arx:", arxReqMsg);

    // 连接Arx,定于webRequestStart消息
    badmiton_ws.subscribe(WS_MSG_TYPE_STARTSTATUS, (info) => {
      if (info[1] == "ok") {
        // 延时3秒调用iframe(arx未完全启动会导致iframe加载失败)
        setTimeout(() => {
          this.arxConnection.iframeUrl = `${info[3]}?id=${info[2]}&api=${info[4]}&csctrl=${SERVERURL}&amp=1`;
          this.arxConnection.arxServerUrl = info[4];
          if (_.isFunction(callback)) {
            callback(this.arxConnection);
          }
          //   this.connectArxServer();
        }, 1000 * 3);
      }
      if (info[1] == "failed") {
        console.log("启动Arx失败!");
        callback(null);
      }
    });
  }

  /**
   * 连接Arx服务
   * @param {*} arxServerUrl
   * @param {*} callback 连接成功回调
   */
  connectArxServer(arxServerUrl, callback) {
    this.arx_ws = new Ws(`${arxServerUrl}/api`);
    console.log("try to connect arx_ws url:", this.arx_ws.url);
    let timerId = setInterval(() => {
      if (this.arx_ws.ws.readyState == 1) {
        // 0-CONNECTING 1-OPEN 2-CLOSING 3-CLOSED
        clearInterval(timerId);
        if (_.isFunction(callback)) {
          callback();
        }
      }
    }, 1000);
  }

  /**
   * 断开arx连接，此时Arx云渲染会被释放
   */
  disconnectArxServer() {
    console.log("YYYY");
    if (this.arx_ws) {
      try {
        this.arx_ws.destroy();
      } catch (ex) {
        console.warn("disconnectArxServer:", ex);
      }
    }
  }

  sendArxMessage(message) {
    console.log("send a message: ", message);
    this.arx_ws.send(message);
  }

  subscribeArxMessage(msg_type, callback) {
    this.arx_ws.subscribe(msg_type, (res) => {
      if (_.isFunction(callback)) {
        callback(res);
      }
    });
  }

  unsubscribeArxMessage(msg_type) {
    this.arx_ws.unsubscribe(msg_type);
  }

  /**
   * 订阅页面监听底板交互推送
   * @param {*} callback 回调阐述交互对象标识
   */
  subscribeArxInteraction(methodName, callback) {
    this.subscribeArxMessage(methodName, (msg) => {
      callback(msg);
    });
  }
  static getInstance() {
    if (!WsApi._instance) {
      WsApi._instance = new WsApi(SERVERURL);
    }
    return WsApi._instance;
  }
}

export default WsApi.getInstance();
