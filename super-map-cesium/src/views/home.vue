<template>
    <div element-loading-text="地图初始化中......" v-loading="loading" class="wrap" element-loading-background="rgba(0, 0, 0, 0.6)">
        <div class="header">
            <div class="headerTitle">数字孪生富水水库可视化模型</div>
        </div>
        <cesium3DMap v-if="tabPosition == 'three'" />
        <openlayMap v-else />
        <div class="threeSwitch">
            <el-radio-group v-model="tabPosition" style="margin-bottom: 30px">
                <el-radio-button label="two">二维</el-radio-button>
                <el-radio-button label="three">三维</el-radio-button>
            </el-radio-group>
        </div>
        <leftCom :mapType='tabPosition' />
    </div>
</template>

<script>
import cesium3DMap from '../components/cesium3DMap'
import openlayMap from '../components/openlayMap'
import leftCom from '../components/leftDialogCom'
export default {
    name: 'home',
    components: {
        cesium3DMap,
        openlayMap,
        leftCom
    },
    data() {
        return {
            isShow: false,
            tabPosition: 'three',
            loading: true,
        }
    },
    watch: {
        tabPosition(newVal, oldVal){
            let that = this
            if (newVal !== 'two') {
                if (localStorage.getItem('initMap') == 'true') {
                    that.loading = true
                }
            } else {
                that.loading = false;
                // localStorage.setItem('initMap', true)
            }
        },

    },
    created() {
        let that = this
        // if (localStorage.getItem('initMap') == true) {
        //     that.loading = true
        // }
        localStorage.setItem('initMap', true)
        this.$bus.on('zhjc', (val) => {
            console.log("jzdt===========", that.loading)
            that.loading = false
        })
    },
    methods: {
    }
}
</script>

<style lang="less" scoped>
.wrap{
  width: 100%;
  height: 100%;
}
.threeSwitch {
    position: fixed;
    top: 90px;
    right: 60px;
}
.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 95px;
    display: flex;
    justify-content: center;
    z-index: 1000;
    color: #fff;
    background: url("@/assets/headBg.png") no-repeat center;
    background-size: 100% 100%;

    .headerTitle {
        height: 63px;
        font-family: AlimamaShuHeiTi;
        font-size: 34px;
        color: #fff;
        line-height: 65px;
        letter-spacing: 3px;
        text-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
        text-align: right;
        font-style: normal;
        text-transform: none;
    }

    .components {
        position: fixed !important;
        width: 100px;
        height: 28px;
        top: 10px;
        left: 32px;
        cursor: pointer;
        background: url("@/assets/comBg.png") no-repeat center;
        background-size: 100% 100%;
    }
}
.fade-enter-active,
.fade-leave-active {
    transition: opacity 2s;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}

.leftDialog {
    position: fixed;
    top: 80px;
    left: 60px;
    width: 320px;
    height: 800px;
    background: url("@/assets/dialogBg.png") no-repeat center;
    background-size: 100% 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: left 0.8s;

    .closeImg {
        position: absolute;
        top: 13px;
        right: 10px;
        width: 20px;
        height: 20px;
        background: url("@/assets/close.png") no-repeat center;
        background-size: 100% 100%;
        cursor: pointer;

        &:hover {
            background: url("@/assets/close.png") no-repeat center;
            background-size: 100% 100%;
        }
    }

    .headTitle {
        width: 100%;
        height: 33px;
        margin-left: 20px;
        font-size: 20px;
        color: #abdfff;
        line-height: 36px;
        text-align: left;
        font-style: normal;
        text-transform: none;
    }

    .firstBlock {
        margin-top: 20px;
        width: 90%;

        .titleBg {
            background: url("@/assets/titleBg.png") no-repeat center;
            background-size: 100% 100%;
            width: 100%;
            height: 22px;
            font-size: 16px;
            color: #a0f0ff;
            line-height: 20px;
            text-align: left;
            font-style: normal;
            padding-left: 20%;
            box-sizing: border-box;
        }

        .cards {
            margin-top: 16px;
            width: 100%;
            height: auto;
            padding: 5%;
            box-sizing: border-box;
            background: rgba(14, 119, 255, 0.15);

            .weatHead {
                text-align: left;
                margin-bottom: 10px;
                font-size: 14px;
                color: #a0f0ff;
            }
        }
    }
}
</style>
