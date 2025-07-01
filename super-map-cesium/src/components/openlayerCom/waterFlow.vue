<template>
    <div v-if="overLayShow">
        <div class="site-box" ref="popupTime">
            <div class="box">
                <h3>{{ siteObj.rvskName }}流量</h3>
                <p>{{ (siteObj.q).toFixed(2) }} m³/s</p>
                <el-progress :percentage="flowRate" color="#6ABAFF" :stroke-width="8" :format="()=>{}"/>
            </div>
            <div class="box">
                <div class="vertical">
                    <el-progress style="top: 30px; left: 20px;" :percentage="waterRess" :format="()=>{}" color="#6ABAFF" :stroke-width="8" />
                </div>
                <div class="waterLevel">
                    <h3>{{ siteObj.rvskName }}水位</h3>
                    <p>{{ (siteObj.z).toFixed(2) }} m</p>
                </div>
            </div>
        </div>
        <div class="play-box">
            <div class="progressBox">
                <div class="elBtn">
                    <i class="el-icon-video-pause" circle style="font-size: 32px; cursor: pointer; color: #409efc; " v-if="curNum" @click="changePause" />
                    <i class="el-icon-video-play" circle style="font-size: 32px; cursor: pointer; color: #409efc; " v-else @click="changePlay" />
                </div>
                <div class="elGress">
                    <el-progress :percentage="percentage" color="#6ABAFF" :format="format" :stroke-width="8" />
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { Vector as VectorSource } from "ol/source";
import { Vector as VectorLayer } from "ol/layer";
import { Fill, Stroke, Style, Text, Icon } from 'ol/style';
import { GeoJSON } from 'ol/format'
import { Feature, Overlay } from 'ol';
import { Point, Circle, LineString } from 'ol/geom';
import CircleStyle from 'ol/style/Circle';
import { getVectorContext } from "ol/render";
import dayjs from "dayjs";
export default {
    data() {
        return {
            siteObj: {
                rvskName: '富水',
                q: 0,
                z: 0
            },
            percentage: 0,
            curNum: false,
            flowRate: 0,
            waterRess: 0,
            overlayPop: null,
            overlayTime: null,
            map:null,
            duration: 0,
            stepTime: 0,
            minTime: null,
            addTime: 0,
            overLayShow: false
        }
    },
    mounted(){
        
        let maxTime = dayjs(new Date()).format('YYYY-MM-DD HH:mm:ss'); //当前时间
        this.minTime = dayjs("2024-07-03 20:00:00"); // 开始时间
        this.duration = dayjs(maxTime).diff(this.minTime, "hour");
        this.stepTime =  100 / this.duration;
        this.addTime =  this.duration / 100;
    },
    watch: {
        percentage: {
            handler(newVal, oldVal) {
                let temps = dayjs(this.minTime).add(newVal * this.addTime, 'hours')
                let curTimes = temps.format('YYYY-MM-DD HH:mm:ss');
            },
        }
    },
    methods: {
        format(val) {
            let temp = val.toFixed(0)
            return temp == 100 ? '0h' : `${temp}h`;
        },
        createdMap(map){
            this.overLayShow = true;
            setTimeout(() => {
                this.map = map;
                this.createOverlay([114.275000000, 29.475000000])
            }, 1000)
            
        },
        changePause() {
            clearInterval(window._time);
            this.curNum = !this.curNum
        },
        changePlay(){
            // this.showPops = true;
            window._time = setInterval(() => {
                
                this.percentage = this.percentage + this.stepTime;
                this.flowRate = this.flowRate + this.stepTime;
                this.waterRess = this.waterRess + this.stepTime;
                this.siteObj.q = this.siteObj.q + this.stepTime;
                this.siteObj.z = this.siteObj.z + this.stepTime;
                if(this.duration <= 100){
                    if (this.percentage >= 100) {
                        this.changePause();
                        this.percentage = 0;
                        this.flowRate = 0;
                        this.waterRess = 0;
                        this.siteObj.q = 0;
                        this.siteObj.z = 0;
                    }
                }else{
                    if (this.percentage > 100) {
                        this.changePause();
                        this.percentage = 0;
                        this.flowRate = 0;
                        this.waterRess = 0;
                        this.siteObj.q = 0;
                        this.siteObj.z = 0;
                    }
                }
                
            }, 1000);
            this.curNum = !this.curNum
        },
        createOverlay(coord) {
            this.overlayTime = new Overlay({
                element: this.$refs.popupTime,
                id: "TimeDialog",
                position: coord,
                positioning: "center-center",
                offset: [0, 0],
                autoPan: {
                    animation: {
                        duration: 250,
                    },
                },
            });
            this.overlayTime.setProperties({ category: "water" });
            this.map.addOverlay(this.overlayTime);
        },
        rmOverlays() {
            this.changePause();
            clearInterval(window._time);
            this.map.removeOverlay(this.overlayTime);
            this.overLayShow = false;
        },
    },
    destroyed(){
        clearInterval(window._time)
    }
}
</script>
<style scoped lang="less">
.site-box {
    display: flex;

    .vertical {
        width: 60%;
        transform: rotate(90deg);
    }

    .box {
        width: 200px;
        margin-right: 20px;
        padding: 15px;
        height: 80px;
        border-radius: 10px;
        flex: 1;
        background-color: #27475c;
        h3 {
            font-size: 14px;
            font-weight: 600;
        }

        p {
            margin-bottom: 2px;
            color: #1791ff;
        }

        .waterLevel {
            margin-left: 20px;
        }
    }
}

.play-box {
    position: absolute;
    left: 30%;
    bottom: 6%;
    width: 48%;
    height: 60px;
    line-height: 60px;
    background-color: #27475c;
    .progressBox{
        display: flex;
        justify-content: space-around;
        align-items: center;
        width: 100%;
        height: 100%;
        .elBtn{
            width: 5%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .elGress{
            flex: 1
        }
    }

    :deep .el-progress__text {
        color: #fff !important;
    }
}
</style>
