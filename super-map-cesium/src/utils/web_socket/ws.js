import EventCenter from "./eventCenter";
import { BASE64, endWith } from "./util";

export default class Ws {
  // 要连接的URL
  url;
  msg_splitter = "|"; // 消息格式是字符串,分隔符用来分割消息
  // WebSocket 实例
  ws;
  // 是否在重连中
  isReconnectionLoading = false;
  // 延时重连的 id
  timeId = null;
  // 是否是用户手动关闭连接
  isCustomClose = false;
  // 错误消息队列
  errorStack = [];
  // 消息管理中心
  eventCenter = new EventCenter();

  constructor(url) {
    this.url = url;
    this.createWs();
  }

  createWs() {
    if ("WebSocket" in window) {
      // 实例化
      this.ws = new WebSocket(this.url);
      // 监听事件
      this.onopen();
      this.onerror();
      this.onclose();
      this.onmessage();
    } else {
      console.log("你的浏览器不支持 WebSocket");
    }
  }

  // 监听成功
  onopen() {
    this.ws.onopen = () => {
      console.log(this.ws, "onopen");
      // 发送成功连接之前所发送失败的消息
      // TODO:解决重发多次问题
      this.errorStack.forEach((message) => {
        this.send(message);
      });
      this.errorStack = [];
      this.isReconnectionLoading = false;
    };
  }

  // 监听错误
  onerror() {
    this.ws.onerror = (err) => {
      console.log(err, "onerror");
      this.reconnection();
      this.isReconnectionLoading = false;
    };
  }

  // 监听关闭
  onclose() {
    this.ws.onclose = () => {
      console.log("onclose");

      // 用户手动关闭的不重连
      if (this.isCustomClose) return;

      this.reconnection();
      this.isReconnectionLoading = false;
    };
  }

  // 接收 WebSocket 消息
  async onmessage() {
    this.ws.onmessage = (event) => {
      try {
        const reader = new window.FileReader();
        reader.readAsDataURL(event.data);
        const that = this;
        reader.onloadend = () => {
          // console.log(reader)
          const base64data = reader.result;
          const blobToSend = base64data.substr(base64data.indexOf(",") + 1);
          // console.log(blobToSend)
          const base64 = new BASE64();
          let res = base64.decode(blobToSend);
          if (endWith(res, "$")) {
            res = res.substring(0, res.length - 1); // 取消消息末尾的$标记
          }
          console.log("received message:", res);
          const data = res.split(that.msg_splitter);
          if (data[0]) {
            that.eventCenter.emit(data[0], data);
          }
        };
      } catch (error) {
        console.log(error, "error");
      }
    };
  }

  // 重连
  reconnection() {
    // 防止重复
    if (this.isReconnectionLoading) return;

    this.isReconnectionLoading = true;
    clearTimeout(this.timeId);
    this.timeId = setTimeout(() => {
      this.createWs();
    }, 3000);
  }

  // 发送消息
  send(message) {
    // 连接失败时的处理
    if (this.ws.readyState !== 1) {
      this.errorStack.push(message);
      return;
    }

    this.ws.send(message);
  }

  // 手动关闭
  close() {
    this.isCustomClose = true;
    this.ws.close();
  }

  // 手动开启
  start() {
    this.isCustomClose = false;
    this.reconnection();
  }

  // 订阅
  subscribe(eventName, cb) {
    this.eventCenter.on(eventName, cb);
  }

  // 取消订阅
  unsubscribe(eventName, cb) {
    this.eventCenter.off(eventName, cb);
  }

  // 销毁
  destroy() {
    this.close();
    this.ws = null;
    this.errorStack = null;
    this.eventCenter = null;
  }
}
