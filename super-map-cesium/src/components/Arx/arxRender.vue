<template>
  <div class="render-container">
    <iframe
      :src="arxPageUrl"
      class="render-iframe"
      ref="renderIframe"
      name="renderIframe"
      frameborder="0"
      scrolling="no"
      title=""
    ></iframe>
    <!-- Loading  -->
    <div v-show="!arxServerConnected" class="loader-wrap">
      <div class="loading">
        <div class="loader" />
        <span ref="loadingText" class="loading-text">云渲染启动中...</span>
      </div>
    </div>
  </div>
</template>
<script>
import ws_api from "@/utils/web_socket/ws_api.js";
export default {
  name: "ArxRender",
  props: {},
  data() {
    return {
      arx_ws: undefined,
      arxServerConnected: false,
      arxPageUrl: undefined,
      arxServerUrl: undefined,
      selectedObjectId: undefined,
      arxRunState: this.runState,
    };
  },
  mounted() {
    this.conectToArc();
  },

  methods: {
    conectToArc() {
      let vm = this;
      ws_api.getArxConnection("flood", 1920, 1080, (con) => {
        if (con == null) {
          this.$refs.loadingText.textContent = "请求云渲染服务失败";
          return;
        }
        this.arxPageUrl = con.iframeUrl;
        this.arxServerUrl = con.arxServerUrl;
        ws_api.connectArxServer(this.arxServerUrl, () => {
          this.arxServerConnected = true;
          vm.$parent.listenersArxHandle();
        });
      });
    },
  },
};
</script>
<style scoped lang="scss">
// //渲染容器
.render-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;

  iframe {
    width: 100%;
    height: 100%;
  }

  .loader-wrap {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    text-align: center;
    background: #010010;

    .loading {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);

      .loading-text {
        color: #fff;
        font-size: 20px;
        margin-top: 15px;
        display: block;
      }

      .loader {
        position: relative;
        height: 80px;
        width: 80px;
        border-radius: 80px;
        border: 3px solid rgba(255, 255, 255, 0.7);
        top: 28%;
        top: -webkit-calc(50% - 43px);
        top: calc(50% - 43px);
        left: 35%;
        left: -webkit-calc(50% - 43px);
        left: calc(50% - 43px);
        -webkit-transform-origin: 50% 50%;
        transform-origin: 50% 50%;
        -webkit-animation: loader 3s linear infinite;
        animation: loader 3s linear infinite;

        &:after {
          content: "";
          position: absolute;
          top: -5px;
          left: 20px;
          width: 11px;
          height: 11px;
          border-radius: 10px;
          background-color: #fff;
        }
      }

      @-webkit-keyframes loader {
        0% {
          -webkit-transform: rotate(0deg);
        }

        100% {
          -webkit-transform: rotate(360deg);
        }
      }

      @keyframes loader {
        0% {
          transform: rotate(0deg);
        }

        100% {
          transform: rotate(360deg);
        }
      }
    }
  }
}
</style>
