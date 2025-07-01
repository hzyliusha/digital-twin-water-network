<template>
    <div>
        <div v-if="isHide" @click="isHide = false" class="expand"></div>
        <transition name="fade">
            <div class="leftDialog" v-if="!isHide">
                <div class="closeImg" @click="isHide = !isHide"></div>
                <div class="headTitle">可视化模组</div>
                <div class="firstBlock">
                    <div class="titleBg">自然背景演变可视化</div>
                    <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">天气</div>
                        <div style="display: flex">
                            <el-checkbox-group v-model="weatherType" @change="skyChange">
                                <el-checkbox label="blueSky" true-label="blueSky" false-label="null">晴天</el-checkbox>
                                <el-checkbox label="cloudSky" true-label="cloudSky-5" false-label="null">小雨</el-checkbox>
                                <el-checkbox label="cloudSky" true-label="cloudSky-10" false-label="null">中雨</el-checkbox>
                                <el-checkbox label="cloudSky" true-label="cloudSky-20" false-label="null">大雨</el-checkbox>
                                <el-checkbox label="cloudSky" true-label="cloudSky-30" false-label="null">暴雨</el-checkbox>
                                <el-checkbox label="cloudSky" true-label="cloudSky-50" false-label="null">特大暴雨</el-checkbox>
                                <el-checkbox label="snowSky" true-label="snowSky-5" false-label="null">小雪</el-checkbox>
                                <el-checkbox label="snowSky" true-label="snowSky-10" false-label="null">中雪</el-checkbox>
                                <el-checkbox label="snowSky" true-label="snowSky-15" false-label="null">大雪</el-checkbox>
                                <el-checkbox label="snowSky" true-label="snowSky-20" false-label="null">暴雪</el-checkbox>
                                <el-checkbox label="snowSky" true-label="snowSky-30" false-label="null">特大暴雪</el-checkbox>
                                <el-checkbox label="fogSky" true-label="fogSky" false-label="null">雾</el-checkbox>
                                <el-checkbox label="nightSky" true-label="nightSky" false-label="null">夜晚</el-checkbox>
                                <!-- <el-radio :label="3">雾</el-radio>
                                <el-radio :label="4">风</el-radio> -->
                            </el-checkbox-group>
                        </div>
                    </div>
                    <!-- <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">其他条件</div>
                        <div style="display: flex">
                            <el-checkbox-group v-model="checkList" @change="otherReuqire">
                                <el-checkbox :label="1">光照</el-checkbox>
                                <el-checkbox :label="2">云层</el-checkbox>
                                <el-checkbox :label="3">季节</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div> -->
                    <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">河道下游，蓄滞洪区淹没分析</div>
                        <div style="display: flex">
                            <el-checkbox-group v-model="floodArr" @change="floodChange">
                                <el-checkbox label="upFlood">下游淹没</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">库区水位</div>
                        <div style="display: flex">
                            <el-slider style="width: 300px" v-model="upDateWater" :min="45" :max="60" :marks="marks" @change="waterZ"></el-slider>
                            <!-- <el-radio-group style="display: flex;flex-wrap: wrap;" v-model="upDateWater" @change="waterZ">
                            <el-radio :label="45">45m</el-radio>
                            <el-radio :label="50">50m</el-radio>
                            <el-radio :label="53">53m</el-radio>
                            <el-radio :label="56">56m</el-radio>
                        </el-radio-group> -->
                        </div>
                    </div>
                    <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">河道警戒线</div>
                        <div style="display: flex">
                            <el-checkbox-group v-model="warnLineModel" @change="warnLine">
                                <el-checkbox label="warn">河道警戒线</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">机组/河坝可视化</div>
                        <div style="display: flex; flex-wrap: wrap">
                            <el-checkbox v-model="MachineryChecked" @change="MachineryClick">机组</el-checkbox>
                            <el-checkbox v-model="DamChecked" @change="DamClick">河坝</el-checkbox>
                            <el-checkbox v-model="drawWater" @change="drawWaterClick">开闸放水</el-checkbox>
                            <el-checkbox v-model="polylineGlowChecked" @change="polylineGlowClick">围栏</el-checkbox>
                            <el-checkbox v-model="PointLightChecked" @change="PointLight">光源</el-checkbox>
                            <el-checkbox v-model="RoamChecked" @change="Roam">漫游</el-checkbox>
<!--                            <el-checkbox v-model="GameEngineChecked" @change="GameEngine">游戏引擎泄洪</el-checkbox>-->
                            <el-checkbox v-model="RisingWaterSurfaceChecked" @change="RisingWaterSurface">水面模拟上升</el-checkbox>
                            <!-- <el-checkbox-group v-model="MachineryCheckList" @change="MachinerySelect">
                                <el-checkbox label="机组">机组</el-checkbox>
                                <el-checkbox label="河坝">河坝</el-checkbox>
                            </el-checkbox-group> -->
                        </div>
                    </div>
                    <!-- <div class="cards" v-if="mapType != 'two'">
                        <div class="weatHead">闸门孔</div>
                        <div style="display: flex">
                            <el-checkbox-group v-model="kArr" @change="kArrChange">
                                <el-checkbox :label="0">全部</el-checkbox>
                                <el-checkbox :label="1">1孔</el-checkbox>
                                <el-checkbox :label="2">2孔</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div> -->
                    <div class="cards" v-if="mapType == 'two'">
                        <div class="weatHead">基础地理实体</div>
                        <div>
                            <el-checkbox-group v-model="geogRegion" @change="geogRegionChange">
                                <el-checkbox label="country">行政区划</el-checkbox>
                                <el-checkbox label="river">大型水库</el-checkbox>
                                <el-checkbox label="river1">中型水库</el-checkbox>
                                <el-checkbox label="river2">河流</el-checkbox>
                                <el-checkbox label="river3">长江</el-checkbox>
                                <el-checkbox label="lake">湖泊</el-checkbox>
                                <el-checkbox label="dike">提防</el-checkbox>
                                <el-checkbox label="xzhq">蓄滞洪区</el-checkbox>
                                <el-checkbox label="lyfw">流域范围(概化图)</el-checkbox>
                                <el-checkbox label="lyfwTransparent">流域范围(影像图)</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="cards" v-if="mapType == 'two'">
                        <div class="weatHead">降雨分布</div>
                        <div>
                            <el-checkbox-group v-model="rainFall" @change="rainFallChange">
                                <el-checkbox label="rainFall">降雨分布</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="cards" v-if="mapType == 'two'">
                        <div class="weatHead">动态路线转移图</div>
                        <div>
                            <el-checkbox-group v-model="routeLineArr" @change="routeLineChange">
                                <el-checkbox label="routeLine">路线转移图</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="cards" v-if="mapType == 'two'">
                        <div class="weatHead">点位分布图</div>
                        <div>
                            <el-checkbox-group v-model="pointArr" @change="pointsChange">
                                <el-checkbox label="point">点位分布图</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                    <div class="cards" v-if="mapType == 'two'">
                        <div class="weatHead">预演演示</div>
                        <div>
                            <el-checkbox-group v-model="previewArr" @change="previewChange">
                                <el-checkbox label="point">预演演示</el-checkbox>
                            </el-checkbox-group>
                        </div>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
import close from '../../assets/close.png';
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
export default {
    name: 'leftCom',
    components: {},
    props: {
        mapType: {
            type: String,
            default: 'two'
        }
    },
    data() {
        return {
            isHide: false,
            weatherType: 'blueSky',
            checkList: [],
            rainFall: [],
            routeLineArr: [],
            pointArr: [],
            previewArr: [],
            floodArr: [],
            kArr: [],
            upDateWater: 45,
            warnLineModel: [],
            MachineryChecked: false,
            DamChecked: false,
            drawWater: false,
            polylineGlowChecked: false,
            PointLightChecked: false, //点光源
            GameEngineChecked: false, //游戏引擎泄洪
            RoamChecked: false,
            marks: {
                45: '45m',
                50: '50m',
                55: '55m',
                60: '60m'
            },
            RisingWaterSurfaceChecked: false //水面缓慢上升
        };
    },
    computed: {
        ...mapGetters(['points', 'routeLine', 'preview']),
        // ...mapState('olMap', ['geogRegion']),
        geogRegion: {
            get() {
                return this.$store.getters.geogRegion;
            },
            set(val) {
                this.$store.commit('olMap/SET_GEOGREGION', val);
            }
        }
    },
    watch: {
        upDateWater(newVal, oldVal) {
            if (newVal >= 60) {
                this.$bus.emit('waterZ', newVal);
                clearInterval(this.timer);
            } else {
                this.$bus.emit('waterZ', newVal);
            }
        }
    },
    created() {
        let that = this;
        // this.$bus.on('zhjc', (val) => {
        //     console.log("jzdt===========", that.loading)
        //     that.loading = false
        // })
    },
    methods: {
        // ...mapActions('olMap',{pointsChange: "getPoints"}),
        ...mapMutations('olMap', { pointsChange: 'SET_POINTS', routeLineChange: 'SET_ISSHOWLINE', previewChange: 'SET_PREVIEW' }),
        ...mapActions('olMap', { geogRegionChange: 'setRegion' }),
        // 三维天气
        skyChange(val) {
            this.$bus.emit('skyChange', val);
        },

        // 淹没
        floodChange(val) {
            this.$bus.emit('floodChange', val);
        },
        // 库区水位高度
        waterZ(val) {
            // console.log(val,this.upDateWater)
            this.$bus.emit('waterZ', val);
        },
        // 河道警戒线
        warnLine(val) {
            this.$bus.emit('warnLine', val);
        },
        //电机透视显示事件
        MachineryClick(val) {
            this.$bus.emit('MachineryClick', val);
        },
        //河坝内部显示事件
        DamClick(val) {
            this.$bus.emit('DamClick', val);
        },
        //开闸放水
        drawWaterClick(val) {
            this.$bus.emit('drawWaterClick', val);
        },
        //围栏
        polylineGlowClick(val) {
            this.$bus.emit('polylineGlowClick', val);
        },
        //光源
        PointLight(val) {
            this.$bus.emit('PointLight', val);
        },
        // 泄水闸
        kArrChange(val) {
            this.$bus.emit('kArrChange', val);
        },
        otherReuqire(val) {
            this.$bus.emit('otherReuqire', val);
        },
        // geogRegionChange(val){
        //     this.$bus.emit('geogRegionChange', val)
        // },
        rainFallChange(val) {
            this.$bus.emit('rainFallChange', val);
        },
        GameEngine(val) {
            this.$bus.emit('GameEngine', val);
        },
        Roam(val) {
            //漫游
            this.$bus.emit('Roam', val);
        },
        RisingWaterSurface(val) {
            if (val) {
                this.timer = setInterval(() => {
                    this.upDateWater++;
                }, 1500);
            } else {
                clearInterval(this.timer);
            }
        }
        // pointsChange(val){
        //     console.log(val,'pointsChange')
        //     // this.$store.commit("olMap/SET_POINTS", val);
        //     this.$store.dispatch("olMap/getPoints", val);

        // }
    }
};
</script>

<style lang="less" scoped>
::v-deep .el-radio__label,
::v-deep .el-checkbox__label {
    color: #fff;
}

::v-deep .el-checkbox {
    margin-right: 20px;
}

::v-deep .el-checkbox-group {
    display: flex;
    flex-wrap: wrap;
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
    left: 10px;
    width: 320px;
    height: 800px;
    background: url('@/assets/dialogBg.png') no-repeat center;
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
        background: url('@/assets/close.png') no-repeat center;
        background-size: 100% 100%;
        cursor: pointer;

        &:hover {
            background: url('@/assets/close.png') no-repeat center;
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
            background: url('@/assets/titleBg.png') no-repeat center;
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
                display: flex;
                text-align: left;
                margin-bottom: 10px;
                font-size: 14px;
                color: #a0f0ff;
            }
        }
    }
}

.expand {
    width: 30px;
    height: 30px;
    cursor: pointer;
    position: absolute;
    z-index: 999;
    top: 90px;
    left: 60px;
    background-image: url('../../assets/close.png');
    transform: rotate(180deg);
}
::v-deep .el-slider__marks-text {
    color: #fff;
}
</style>
